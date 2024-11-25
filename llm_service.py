# llm_service.py

import os
import warnings
from io import StringIO
import asyncio
import datetime
import hashlib
import shutil

import fitz
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.messages import HumanMessage
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
from settings import OPENAI_API_KEY, MODEL_NAME, CHAT_HISTORY_LEVEL, DOCS_IN_RETRIEVER
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
        Returns a tuple (response: str, source_files: list or None)
        """
        if not hasattr(self, 'vector_store') or self.vector_store is None:
            logger.warning("Vector store is not loaded. Prompting to set the folder path and load documents.")
            return (
                "Please set the folder path using /folder and ensure documents are loaded.",
                None,
            )

        # Ensure chat_history is a list
        if chat_history is None:
            chat_history = []

        # Create the retriever with k=DOCS_IN_RETRIEVER
        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": DOCS_IN_RETRIEVER}
        )
        logger.debug("Retriever created from vector store.")

        # Create the history-aware retriever
        retriever_prompt = ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                (
                    "user",
                    "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation",
                ),
            ]
        )

        history_aware_retriever = create_history_aware_retriever(
            llm=self.llm, retriever=retriever, prompt=retriever_prompt
        )
        logger.debug("History-aware retriever created.")

        # Create the question-answering chain
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
        logger.debug("Prompt template for QA chain created.")

        question_answer_chain = create_stuff_documents_chain(self.llm, prompt_template)
        logger.debug("Question-answering chain created.")

        # Create the retrieval chain using create_retrieval_chain
        rag_chain = create_retrieval_chain(
            retriever=history_aware_retriever, combine_docs_chain=question_answer_chain
        )
        logger.debug("Retrieval-Augmented Generation (RAG) chain created.")

        # Run the chain with the provided prompt and chat history
        result = rag_chain.invoke({"input": prompt, "chat_history": chat_history})
        logger.debug("RAG chain invoked with user prompt.")

        answer = result.get("answer", "")
        sources = result.get("context", [])

        if not sources:
            logger.debug("No sources retrieved for the prompt.")
            return answer, None

        source_files = set(
            [doc.metadata["source"] for doc in sources if "source" in doc.metadata]
        )

        # Build the references
        references = {}
        for doc in sources:
            filename = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "Unknown")
            if filename not in references:
                references[filename] = set()
            references[filename].add(page)

        # Implement similarity threshold
        is_relevant = self.is_prompt_relevant_to_documents(prompt, sources)

        if is_relevant:
            answer_with_references = (
                    answer + "\n\n------------------" + "\nReferences:\n"
            )

            for doc_name, pages in references.items():
                pages_list = sorted(pages)
                pages_str = ", ".join(str(page) for page in pages_list)
                answer_with_references += f"{doc_name}, pages: {pages_str}\n"

            logger.debug("Similarity threshold met. References appended to the answer.")
            return parser_html(answer_with_references), source_files
        else:
            logger.debug("Similarity threshold not met. Returning answer without references.")
            return parser_html(answer), None

    def is_prompt_relevant_to_documents(self, prompt, sources):
        """
        Determine if the prompt is relevant to the retrieved documents.
        Implement a similarity check or any other logic as needed.
        For demonstration, we'll perform a simple keyword overlap.
        """
        try:
            # Extract keywords from the prompt
            prompt_keywords = set(prompt.lower().split())

            # Extract keywords from the sources
            source_text = " ".join([doc.page_content.lower() for doc in sources])
            source_keywords = set(source_text.split())

            # Calculate overlap
            overlap = prompt_keywords.intersection(source_keywords)

            # Define a threshold for relevance
            relevance_threshold = 0.1  # 10% overlap

            if len(prompt_keywords) == 0:
                logger.debug("No keywords extracted from the prompt.")
                return False

            similarity_ratio = len(overlap) / len(prompt_keywords)
            logger.debug(f"Similarity ratio: {similarity_ratio}")

            return similarity_ratio >= relevance_threshold
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

                elif filename.endswith(".docx"):
                    content = self.load_word_file(file_path)
                    logger.debug(f"Loaded content from Word '{filename}'")

                elif filename.endswith(".xlsx"):
                    content = self.load_excel_file(file_path)
                    logger.debug(f"Loaded content from Excel '{filename}'")

                else:
                    logger.debug(f"Unsupported file type for '{filename}'. Skipping.")
                    continue  # Skip unsupported file types

                # Limit content to first 2000 characters to avoid long prompts
                content_sample = content[:2000]
                logger.debug(f"Prepared content sample for '{filename}'")

                # Generate AI description and document type
                prompt = (
                    "Please analyze the following document content and provide the document type and a brief description in the following format:\n\n"
                    "Document Type: [document type]\n"
                    "Description: [description]\n\n"
                    "Content:\n"
                    f"{content_sample}"
                )

                try:
                    response = self.llm(prompt)
                    logger.debug(f"LLM response for '{filename}': {response}")
                except Exception as e:
                    logger.error(f"Error generating response from LLM for '{filename}': {e}")
                    response = ""

                # Extract description and document type from response
                document_type = ""
                description = ""
                lines = response.strip().split("\n")
                for line in lines:
                    if line.lower().startswith("document type:"):
                        document_type = line[len("document type:"):].strip()
                    elif line.lower().startswith("description:"):
                        description = line[len("description:"):].strip()

                # Append metadata as a dictionary to the list
                metadata_list.append(
                    {
                        "filename": filename,
                        "path_file": file_path,
                        "document_type": document_type,
                        "date_modified": date_modify_str,
                        "description": description,
                    }
                )
                logger.info(f"Extracted metadata for '{filename}': Type='{document_type}', Description='{description}'")

            # After processing all files, mark files as deleted if they are not in the folder
            db_service.mark_files_as_deleted(existing_file_paths)
            logger.debug("Completed metadata extraction and database update.")

        except Exception as e:
            logger.exception(f"Error in get_metadata: {e}")

        return metadata_list
