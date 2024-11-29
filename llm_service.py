# llm_service.py

import os
import warnings
from io import StringIO
import asyncio
import datetime
import hashlib
import shutil
import numpy as np

import fitz
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.llm import LLMChain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
from langchain.chains.combine_documents import create_stuff_documents_chain
import tiktoken
from pymupdf.mupdf import ll_pdf_lookup_substitute_font_outparams

import text
from db_service import DatabaseService
from settings import OPENAI_API_KEY, MODEL_NAME, CHAT_HISTORY_LEVEL, DOCS_IN_RETRIEVER, RELEVANCE_THRESHOLD_DOCS, \
    RELEVANCE_THRESHOLD_PROMPT
from decorators import log_errors
from helpers import current_timestamp, parser_html
from pathlib import Path
import logging

# Initialize logger
logger = logging.getLogger(__name__)

class LLMService:

    def __init__(self, model_name=MODEL_NAME):
        try:
            self.llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name=model_name)
            self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            self.vector_store = None  # Initialize as None; to be loaded later
            logger.info(f"LLMService initialized with model '{model_name}'.")
        except Exception as e:
            logger.exception(f"Failed to initialize LLMService: {str(e)}")
            raise

    def _get_vector_store_path(self, folder_path):
        """
        Generate the vector store directory path within the knowledge base folder.
        """
        return Path(folder_path) / "vector_store"

    def save_vector_store(self, folder_path):
        """
        Save the current vector store to disk within the specified knowledge base folder.
        """
        vector_store_dir = self._get_vector_store_path(folder_path)
        try:
            vector_store_dir.mkdir(parents=True, exist_ok=True)
            if hasattr(self, 'vector_store') and self.vector_store:
                self.vector_store.save_local(str(vector_store_dir))
                logger.info(f"Vector store saved to {vector_store_dir}")
            else:
                logger.warning("No vector_store attribute found or it is None.")
        except Exception as e:
            logger.error(f"Failed to save vector store to {vector_store_dir}: {e}")
            raise

    @log_errors(default_return=(False, "An error occurred while indexing documents."))
    def load_vector_store(self, folder_path):
        """
        Load a saved vector store from disk within the specified knowledge base folder.
        """
        vector_store_dir = self._get_vector_store_path(folder_path)
        if vector_store_dir.exists() and vector_store_dir.is_dir():
            try:
                # ⚠️ Security Warning: Ensure the vector store is from a trusted source before enabling dangerous deserialization.
                self.vector_store = FAISS.load_local(
                    str(vector_store_dir),
                    self.embeddings,
                    allow_dangerous_deserialization=True  # Enable dangerous deserialization
                )
                logger.info(f"Loaded vector store from {vector_store_dir}")
                return True
            except Exception as e:
                logger.error(f"Failed to load vector store from {vector_store_dir}: {str(e)}")
                return False
        else:
            logger.info(f"No saved vector store found in {vector_store_dir}")
            return False

    @log_errors(default_return=(False, "An error occurred while indexing documents."))
    def load_and_index_documents(self, folder_path):
        """
        Load and index documents from the specified folder_path.
        If a saved vector store exists, load it. Otherwise, load documents, index them, and save the vector store.
        Returns a tuple (success: bool, message: str).
        """
        try:
            logger.debug(f"Starting load_and_index_documents for folder_path='{folder_path}'")
            # Check if vector store already exists
            if self.load_vector_store(folder_path):
                logger.info(f"Vector store loaded from existing files in '{folder_path}'")
                return (True, "Vector store loaded from existing files.")

            documents = []
            found_valid_file = False

            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)

                if filename.lower().endswith(".pdf"):
                    try:
                        loader = PyMuPDFLoader(file_path)
                        docs = loader.load()
                        for doc in docs:
                            doc.metadata["source"] = filename
                            documents.append(doc)
                        found_valid_file = True
                        logger.info(f"Loaded PDF document: {filename}")
                    except Exception as e:
                        logger.error(f"Error loading PDF file '{filename}': {str(e)}")

                elif filename.lower().endswith(".docx"):
                    try:
                        content = self.load_word_file(file_path)
                        doc = Document(page_content=content, metadata={"source": filename})
                        documents.append(doc)
                        found_valid_file = True
                        logger.info(f"Loaded Word document: {filename}")
                    except Exception as e:
                        logger.error(f"Error loading Word file '{filename}': {str(e)}")

                elif filename.lower().endswith(".xlsx"):
                    try:
                        content = self.load_excel_file(file_path)
                        doc = Document(page_content=content, metadata={"source": filename})
                        documents.append(doc)
                        found_valid_file = True
                        logger.info(f"Loaded Excel document: {filename}")
                    except Exception as e:
                        logger.error(f"Error loading Excel file '{filename}': {str(e)}")

                else:
                    logger.debug(f"Skipped unsupported file type: {filename}")

            if not found_valid_file:
                logger.warning("No valid files found in the folder. Please provide PDF, Word, or Excel files.")
                return (False, "No valid files found in the folder. Please provide PDF, Word, or Excel files.")

            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            split_docs = text_splitter.split_documents(documents)
            logger.info(f"Split documents into {len(split_docs)} chunks.")

            self.vector_store = FAISS.from_documents(split_docs, self.embeddings)
            logger.info("Documents successfully indexed.")

            # Save the newly created vector store
            self.save_vector_store(folder_path)

            return (True, "Documents successfully indexed and vector store saved.")

        except Exception as e:
            logger.error(f"Error during load_and_index_documents: {str(e)}")
            return (False, str(e))

    @log_errors(default_return=("An error occurred while generating a response.", None))
    def generate_response(self, prompt, chat_history=None):
        """
        Generate a response to the user's prompt using the LLM and the vector store.
        Returns a tuple (response: str, source_files: list or None, suggestions: list or None)
        """
        if not hasattr(self, 'vector_store') or self.vector_store is None:
            logger.warning("Vector store is not loaded. Prompting to set the folder path and load documents.")
            return (
                "Please set the folder path using /folder and ensure documents are loaded.",
                None,
                None
            )

        # Ensure chat_history is a list
        if chat_history is None:
            chat_history = []

        # Retrieve documents with similarity scores
        retrieved_docs_with_scores = self.vector_store.similarity_search_with_score(
            prompt, k=DOCS_IN_RETRIEVER
        )
        logger.debug("Retrieved documents with similarity scores.")

        retrieved_docs = [doc for doc, _ in retrieved_docs_with_scores]

        # Compute embeddings similarity
        relevance_scores = self.compute_embeddings_similarity(prompt, retrieved_docs)

        # Filter relevant documents based on similarity threshold
        relevant_docs = [doc for doc, similarity in relevance_scores if similarity >= RELEVANCE_THRESHOLD_DOCS]

        if not relevant_docs:
            logger.debug("No relevant documents found for the prompt.")
            answer = "I'm sorry, I could not find relevant information to answer your question."
            return parser_html(answer), None, None

        # Build the context string
        context_str = "\n\n".join([doc.page_content for doc in relevant_docs])

        # Create the prompt template
        system_prompt = (
            "You are a project assistant from the consultant side on design and construction projects."
            " If you don't know the answer, say that you don't know."
            " Do not include references to the source documents in your answer."
            f" If you need to use the current date, today is {current_timestamp()}."
            " If the prompt includes a request to provide a link to documents in context, respond with: Please follow the link below:"
            " Format your response using Telegram-compatible HTML. Use only supported tags (<b>, <strong>, <i>, <em>, <a>, <u>, <s>, <code>, <pre>, <tg-spoiler>) and use \\n for line breaks instead of <br>."
            " Use the following pieces of retrieved context to answer the question."
            "\n\n{context}"
        )

        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
            ]
        )

        # Create the chain using RunnableSequence
        chain = prompt_template | self.llm

        # Call the chain with the prompt, chat_history, and context
        result = chain.invoke({"input": prompt, "chat_history": chat_history, "context": context_str})

        # Extract the answer text
        if isinstance(result, BaseMessage):
            answer = result.content
        elif isinstance(result, str):
            answer = result
        else:
            logger.error(f"Unexpected result type from chain: {type(result)}")
            answer = str(result)

        # Build the references
        references = {}
        for doc in relevant_docs:
            filename = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "Unknown")
            if filename not in references:
                references[filename] = set()
            references[filename].add(page)

        # Implement similarity threshold
        is_relevant = self.is_prompt_relevant_to_documents(relevance_scores)

        if is_relevant:
            # Build the answer with references
            answer_with_references = (
                    answer + "\n\n------------------" + "\nReferences (/references):\n"
            )
            for doc_name, pages in references.items():
                pages_list = sorted(pages)
                pages_str = ", ".join(str(page) for page in pages_list)
                answer_with_references += f"{doc_name}, pages: {pages_str}\n"
            logger.debug(f"References appended to the answer. RELEVANCE_THRESHOLD_DOCS: {RELEVANCE_THRESHOLD_DOCS}")
            response = parser_html(answer_with_references)
            source_files = set([doc.metadata.get("source") for doc in relevant_docs])
        else:
            logger.debug("Similarity threshold not met. Returning answer without references.")
            response = parser_html(answer)
            source_files = None

        # Generate suggestions based on user prompt and LLM response
        suggestions = self.generate_suggestions(user_prompt=prompt, llm_response=answer, n=3)

        return response, source_files, suggestions

    def generate_suggestions(self, user_prompt, llm_response, n=3):
        """
        Generate up to n suggestions to help the user continue the conversation.
        Suggestions are based on the user prompt and the LLM's response.

        Parameters:
            user_prompt (str): The original prompt from the user.
            llm_response (str): The response generated by the LLM.
            n (int): Maximum number of suggestions to generate.

        Returns:
            List[str] or None: A list of suggestion strings or None if no suggestions are needed.
        """
        try:
            logger.debug("Generating suggestions based on user prompt and LLM response.")

            # Define the prompt for generating suggestions
            suggestion_prompt = (
                "Given the following user prompt and LLM response, determine if additional information is needed to help the user fulfill their request and continue the conversation effectively. "
                "If yes, provide up to {n} additional prompts based on key concepts in the response, such as 'learn more about ...', 'how to determine ...', 'how to calculate ...', etc., that the user can use to gather more information. "
                "If no additional prompts are needed, respond with 'No suggestions needed'.\n\n"
                f"User Prompt: {user_prompt}\n\n"
                f"LLM Response: {llm_response}\n\n"
                "Suggestions:"
            ).format(n=n)

            # Generate the suggestions using the LLM
            # Use predict method for simplicity
            generated_text = self.llm.predict(suggestion_prompt)

            # Extract the text from the response
            if generated_text.strip().lower() == "no suggestions needed.":
                logger.debug("LLM determined that no suggestions are needed.")
                return None

            # Split the suggestions by lines or numbers
            suggestions = []
            for line in generated_text.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                # Remove leading numbers or bullets
                if line[0].isdigit() and '.' in line:
                    line = line.split('.', 1)[1].strip()
                elif line.startswith('-'):
                    line = line[1:].strip()
                suggestions.append(line)

            # Limit to n suggestions
            suggestions = suggestions[:n]

            if not suggestions:
                logger.debug("LLM did not provide any valid suggestions.")
                return None

            logger.debug(f"Generated suggestions: {suggestions}")
            return suggestions
        except Exception as e:
            logger.exception(f"Error generating suggestions: {str(e)}")
            return None

    def compute_embeddings_similarity(self, prompt, documents):
        """
        Compute the cosine similarity between the prompt and each document.
        Returns a list of tuples (document, similarity_score)
        """
        try:
            # Get embedding of the prompt
            prompt_embedding = self.embeddings.embed_query(prompt)
            prompt_embedding = np.array(prompt_embedding)

            relevance_scores = []
            for doc in documents:
                doc_embedding = self.embeddings.embed_query(doc.page_content)
                doc_embedding = np.array(doc_embedding)

                # Compute cosine similarity
                dot_product = np.dot(prompt_embedding, doc_embedding)
                norm_prompt = np.linalg.norm(prompt_embedding)
                norm_doc = np.linalg.norm(doc_embedding)
                if norm_prompt == 0 or norm_doc == 0:
                    similarity = 0.0
                else:
                    similarity = dot_product / (norm_prompt * norm_doc)
                relevance_scores.append((doc, similarity))

            return relevance_scores

        except Exception as e:
            logger.exception(f"Error computing embeddings similarity: {str(e)}")
            return []

    def is_prompt_relevant_to_documents(self, relevance_scores, relevance_threshold=RELEVANCE_THRESHOLD_PROMPT):
        """
        Determine if the prompt is relevant to the retrieved documents based on embeddings similarity.
        """
        try:
            max_similarity = max([similarity for _, similarity in relevance_scores], default=0.0)
            logger.debug(f"Maximum similarity: {max_similarity}, RELEVANCE_THRESHOLD_PROMPT: {RELEVANCE_THRESHOLD_PROMPT}")
            return max_similarity >= relevance_threshold
        except Exception as e:
            logger.exception(f"Error in is_prompt_relevant_to_documents: {str(e)}")
            return False

    def get_empty_docs(self, folder_path):
        """
        Scan through all PDF files in the specified folder and return a list of filenames
        that contain one or more empty pages.
        """
        empty_docs = []
        user_id = None  # You can modify this if you have user context

        # Suppress warnings from PyMuPDFLoader if necessary
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            for filename in os.listdir(folder_path):
                if not filename.lower().endswith(".pdf"):
                    continue  # Skip non-PDF files

                file_path = os.path.join(folder_path, filename)

                try:
                    # Open the PDF using PyMuPDF
                    with fitz.open(file_path) as doc:
                        for page_num in range(len(doc)):
                            page = doc.load_page(page_num)
                            text = page.get_text().strip()

                            if not text:
                                # Empty page found
                                logger.info(f"Empty content on page {page_num} of document '{filename}'")
                                empty_docs.append(filename)
                                break  # No need to check further pages in this document

                except Exception as e:
                    logger.error(f"Error processing '{filename}': {e}")
                    continue  # Skip to the next file in case of an error

        return empty_docs

    @log_errors(default_return=[])
    def get_metadata(self, folder_path, db_service):
        """
        Extract metadata from documents in the specified folder and update the database.
        """
        metadata_list = []
        existing_file_paths = []

        try:
            logger.debug(f"Starting metadata extraction for folder_path='{folder_path}'")
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)

                # Skip directories
                if os.path.isdir(file_path):
                    logger.debug(f"Skipping directory: {filename}")
                    continue

                # Get the last modified time of the file from filesystem
                timestamp = os.path.getmtime(file_path)
                file_date_modified = datetime.datetime.fromtimestamp(timestamp)
                date_modify_str = file_date_modified.strftime("%Y-%m-%d %H:%M:%S")

                # Get dates from database
                db_date_modified, date_of_analysis = db_service.get_file_dates(file_path)

                if date_of_analysis:
                    # Compare file's date_modified with date_of_analysis
                    if file_date_modified <= date_of_analysis:
                        # File has not been modified since last analysis; skip processing
                        logger.info(f"Skipping '{filename}'; no changes detected.")
                        continue
                    else:
                        logger.info(f"Re-analyzing '{filename}'; file has been modified.")
                else:
                    logger.info(f"Analyzing new file: '{filename}'")

                # Load content based on file type
                if filename.endswith(".pdf"):
                    loader = PyMuPDFLoader(file_path)
                    docs = loader.load()
                    content = " ".join([doc.page_content for doc in docs])
                    logger.debug(f"Loaded content from PDF '{filename}'")

                else:
                    logger.debug(f"Unsupported file type for '{filename}'. Skipping.")
                    continue  # Skip unsupported file types

                # Limit content to first 2000 characters to avoid long prompts
                content_sample = content[:2000]
                logger.debug(f"Prepared content sample for '{filename}'")

                # Generate AI description, document type, and language
                prompt = (
                    "Analyze the following document content and provide the document type, a brief description, and the language (select one primary language if the document is multilingua) in the following format:\n\n"
                    "Document Type: [document type]\n"
                    "Description: [description]\n"
                    "Language: [language]\n\n"
                    "Content:\n"
                    f"{content_sample}"
                )

                try:
                    response = self.llm.invoke(prompt)  # Adjust this method if necessary
                    response_text = response.content  # Access the text content
                    logger.debug(f"LLM response for '{filename}': {response_text}")
                except Exception as e:
                    logger.error(f"Error generating response from LLM for '{filename}': {e}")
                    response_text = ""

                # Extract description, document type, and language from response
                document_type = ""
                description = ""
                language = ""
                if isinstance(response_text, str):
                    lines = response_text.strip().split("\n")
                    for line in lines:
                        if line.lower().startswith("document type:"):
                            document_type = line[len("document type:"):].strip()
                        elif line.lower().startswith("description:"):
                            description = line[len("description:"):].strip()
                        elif line.lower().startswith("language:"):
                            language = line[len("language:"):].strip()
                else:
                    logger.error(f"Unexpected response type for '{filename}': {type(response_text)}")

                # Append metadata as a dictionary to the list
                metadata_list.append(
                    {
                        "filename": filename,
                        "path_file": file_path,
                        "document_type": document_type,
                        "date_modified": date_modify_str,
                        "description": description,
                        "language": language,  # New language field
                    }
                )
                logger.info(
                    f"Extracted metadata for '{filename}': Type='{document_type}', Description='{description}', Language='{language}'")

            # After processing all files, mark files as deleted if they are not in the folder
#            db_service.mark_files_as_deleted(existing_file_paths)
            logger.debug("Completed metadata extraction and database update.")

        except Exception as e:
            logger.exception(f"Error in get_metadata: {e}")

        return metadata_list
