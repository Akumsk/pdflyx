# handlers.py

import logging
import os
import uuid
import asyncio

import aiofiles
from telegram import (
    Update,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Document,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    Updater,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from telegram.constants import ParseMode

from settings import CHAT_HISTORY_LEVEL, knowledge_base_paths, SUPPORTED_LANGUAGES
from db_service import DatabaseService
from llm_service import LLMService
from helpers import messages_to_langchain_messages, get_language_code
import text
from text import KnowledgeBaseResponses, CommandDescriptions


# Decorators:
def authorized_only(func):
    async def wrapper(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user = update.effective_user
        user_id = user.id
        user_name = user.full_name
        language_code = user.language_code

        if "db_service" not in context.user_data:
            context.user_data["db_service"] = DatabaseService()

        db_service = context.user_data["db_service"]

        # Save or update user info
        db_service.save_user_info(user_id, user_name, language_code)

        # Check if user has access
        if not db_service.check_user_access(user_id):
            system_response = text.Responses.access_denied()
            if update.message:
                await update.message.reply_text(system_response)
            elif update.callback_query:
                await update.callback_query.answer(
                    system_response,
                    show_alert=True,
                )
            return
        else:
            # Update last_active
            db_service.update_last_active(user_id)

        return await func(self, update, context, *args, **kwargs)

    return wrapper


def initialize_services(func):
    async def wrapper(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        if "db_service" not in context.user_data:
            context.user_data["db_service"] = DatabaseService()
        if "llm_service" not in context.user_data:
            context.user_data["llm_service"] = LLMService()
        if "user_id" not in context.user_data:
            context.user_data["user_id"] = update.effective_user.id
        if "user_name" not in context.user_data:
            context.user_data["user_name"] = update.effective_user.full_name
        if "language_code" not in context.user_data:
            context.user_data["language_code"] = update.effective_user.language_code

        # Access db_service
        db_service = context.user_data["db_service"]
        user_id = context.user_data["user_id"]

        # Fetch current_language from the database
        current_language = db_service.get_current_language(user_id)
        if current_language:
            context.user_data["language"] = current_language
        else:
            # If current_language is not set, initialize it with language_code
            language_code = context.user_data["language_code"]
            context.user_data["language"] = language_code
            db_service.update_current_language(user_id, language_code)

        return await func(self, update, context, *args, **kwargs)

    return wrapper


def ensure_documents_indexed(func):
    async def wrapper(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        if not context.user_data.get("vector_store_loaded", False):
            system_response = text.ContextErrors.documents_not_indexed()
            await update.message.reply_text(system_response)
            return ConversationHandler.END
        valid_files_in_folder = context.user_data.get("valid_files_in_folder", [])
        if not valid_files_in_folder:
            system_response = text.ContextErrors.no_valid_documents()
            await update.message.reply_text(system_response)
            return ConversationHandler.END
        return await func(self, update, context, *args, **kwargs)

    return wrapper


def log_event(event_type):
    def decorator(func):
        async def wrapper(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
        ):
            # Before executing the handler function
            user_id = update.effective_user.id

            # Extract user_message based on the type of update
            if update.message:
                user_message = update.message.text
            elif update.callback_query:
                user_message = update.callback_query.data
            else:
                user_message = ""

            conversation_id = context.user_data.get("conversation_id")
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                context.user_data["conversation_id"] = conversation_id

            # Initialize system_response
            system_response = context.user_data.get("system_response", "")

            try:
                # Execute the handler function
                result = await func(self, update, context, *args, **kwargs)
                # After executing the handler function, retrieve system_response
                system_response = context.user_data.get("system_response", system_response)
            except Exception as e:
                # Log the exception
                logging.error(f"Exception in handler function {func.__name__}: {e}")
                # Set system_response to a generic error message
                language = context.user_data.get("language", "English")
                system_response = text.Responses.generic_error(language=language)
                # Send error message to the user
                if update.message:
                    await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
                elif update.callback_query:
                    await update.callback_query.message.reply_text(system_response, parse_mode=ParseMode.HTML)
                # Set system_response in context.user_data
                context.user_data["system_response"] = system_response
                result = None  # Or re-raise the exception if desired

            # Access db_service
            db_service = context.user_data.get("db_service")
            if db_service:
                db_service.save_event_log(
                    user_id=user_id,
                    event_type=event_type,
                    user_message=user_message,
                    system_response=system_response,
                    conversation_id=conversation_id,
                )
            else:
                logging.error("db_service not found in context.user_data")

            return result

        return wrapper

    return decorator


WAITING_FOR_FOLDER_PATH = range(1)


class BotHandlers:
    def __init__(self):
        pass

    async def post_init(self, application):
        """
        Initializes bot commands with multilingual support.
        """
        for language in SUPPORTED_LANGUAGES:
            commands = CommandDescriptions.get_commands(language=language)
            language_code = get_language_code(language)
            try:
                await application.bot.set_my_commands(
                    commands,
                    language_code=language_code
                )
                logging.info(f"Commands set for language: {language} ({language_code})")
            except Exception as e:
                logging.error(f"Failed to set commands for {language} ({language_code}): {e}")

    @initialize_services
    @log_event(event_type="command")
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = context.user_data["user_id"]
        user_name = context.user_data["user_name"]
        language_code = context.user_data["language_code"]

        db_service = context.user_data["db_service"]

        # Save or update user info
        db_service.save_user_info(user_id, user_name, language_code)

        language = context.user_data.get("language", "English")
        system_response = text.Greetings.first_time(language=language, user_name=user_name)
        await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)

        # Store system_response in context.user_data
        context.user_data["system_response"] = system_response

    @authorized_only
    @initialize_services
    @log_event(event_type="command")
    async def language(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /language command."""
        keyboard = [
            [InlineKeyboardButton("English", callback_data="set_language:English")],
            [InlineKeyboardButton("Русский", callback_data="set_language:Russian")],
            [InlineKeyboardButton("Indonesian", callback_data="set_language:Indonesian")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Use language from context.user_data
        current_language = context.user_data.get("language", "English")
        system_response = text.LanguageResponses.select_language_prompt(current_language)

        await update.message.reply_text(system_response, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        context.user_data["system_response"] = system_response

    @authorized_only
    @initialize_services
    @log_event(event_type="inline_button")
    async def set_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set the user's preferred language."""
        query = update.callback_query
        await query.answer()
        data = query.data
        if data.startswith("set_language:"):
            selected_language = data[len("set_language:"):]
            context.user_data["language"] = selected_language
            user_id = update.effective_user.id

            # Access the db_service from context.user_data
            db_service = context.user_data.get("db_service")
            if db_service:
                # Update the current_language in the database
                db_service.update_current_language(user_id, selected_language)
            else:
                logging.error("db_service not found in context.user_data")

            # Use language-specific response
            system_response = text.LanguageResponses.language_set_success(selected_language)
            await query.message.reply_text(system_response)
            context.user_data["system_response"] = system_response
        else:
            system_response = text.Responses.unknown_command(language=context.user_data.get("language", "English"))
            await query.message.reply_text(system_response)
            context.user_data["system_response"] = system_response

    @authorized_only
    @initialize_services
    @log_event(event_type="command")
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /status command."""
        llm_service = context.user_data["llm_service"]
        user_name = update.effective_user.full_name
        folder_path = context.user_data.get("folder_path", "")
        valid_files_in_folder = context.user_data.get("valid_files_in_folder", [])
        context_source = context.user_data.get("context_source", "none")
        language = context.user_data.get("language", "English")

        # Find the knowledge base name from the folder_path
        knowledge_base_name = None
        for kb_name, kb_path in knowledge_base_paths.items():
            if kb_path == folder_path:
                knowledge_base_name = kb_name
                break

        if context_source in ["folder", "upload"]:
            if knowledge_base_name and valid_files_in_folder:
                file_list = "\n".join(valid_files_in_folder)
                # Retrieve list of empty documents
                empty_list = llm_service.get_empty_docs(folder_path)
                if context_source == "folder":
                    system_response = text.Status.knowledge_base_set(
                        user_name,
                        knowledge_base_name,
                        file_list,
                        empty_list if empty_list else None,
                        language=language,
                    )
                elif context_source == "upload":
                    system_response = text.Status.knowledge_base_set(
                        user_name,
                        "your uploaded documents",
                        file_list,
                        empty_list if empty_list else None,
                        language=language,
                    )
            else:
                if context_source == "folder" and knowledge_base_name:
                    system_response = text.Status.knowledge_base_no_files(
                        user_name, knowledge_base_name,
                        language=language,
                    )
                elif context_source == "upload":
                    system_response = text.Status.knowledge_base_no_files(
                        user_name, "your uploaded documents", language=language
                    )
                else:
                    system_response = text.Status.no_knowledge_base_selected(user_name, language=language)
        else:
            system_response = text.Status.no_knowledge_base_selected(user_name, language=language)

        await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)

    @authorized_only
    @initialize_services
    @log_event(event_type="command")
    async def knowledge_base(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /knowledge_base command."""
        # Create a keyboard from the keys of the knowledge_base_paths dictionary
        language = context.user_data.get("language", "English")
        keyboard = [
            [InlineKeyboardButton(kb_name, callback_data=f"set_knowledge:{kb_name}")]
            for kb_name in knowledge_base_paths.keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        system_response = text.KnowledgeBaseResponses.select_knowledge_base(language=language)
        await update.message.reply_text(
            system_response, reply_markup=reply_markup, parse_mode=ParseMode.HTML
        )

    @authorized_only
    @initialize_services
    @log_event(event_type="inline_button")
    async def set_knowledge_base(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Set the folder path based on the user's knowledge base selection."""
        query = update.callback_query
        language = context.user_data.get("language", "English")
        await query.answer()
        data = query.data
        if data.startswith("set_knowledge:"):
            selection = data[len("set_knowledge:"):]
            folder_path = knowledge_base_paths.get(selection, None)
            if folder_path is None:
                system_response = KnowledgeBaseResponses.unknown_knowledge_base()
                await query.message.reply_text(system_response)
                context.user_data["system_response"] = system_response
                return

            # Set the folder path and process the documents
            context.user_data["folder_path"] = folder_path
            context.user_data["context_source"] = (
                "folder"  # Set context source as folder
            )

            # Index the documents in the folder
            llm_service = context.user_data["llm_service"]
            valid_files_in_folder = [
                f
                for f in os.listdir(folder_path)
                if f.lower().endswith((".pdf", ".docx", ".xlsx"))
            ]
            context.user_data["valid_files_in_folder"] = valid_files_in_folder
            if not valid_files_in_folder:
                await query.message.reply_text(
                    KnowledgeBaseResponses.no_valid_files_in_knowledge_base(language=language), parse_mode=ParseMode.HTML
                )
                return
            index_status = llm_service.load_and_index_documents(folder_path)
            if index_status != "Documents successfully indexed.":
                logging.error(f"Error during load_and_index_documents: {index_status}")
                await query.message.reply_text(KnowledgeBaseResponses.indexing_error(language=language), parse_mode=ParseMode.HTML)
                return
            context.user_data["vector_store_loaded"] = True
            system_response = KnowledgeBaseResponses.knowledge_base_set_success(selection, language=language)
            await query.message.reply_text(system_response, parse_mode=ParseMode.HTML)
            context.user_data["system_response"] = system_response
        else:
            system_response = KnowledgeBaseResponses.unknown_command(language=language)
            await query.message.reply_text(system_response, parse_mode=ParseMode.HTML)
            context.user_data["system_response"] = system_response

    @authorized_only
    @initialize_services
    @log_event(event_type="command")
    async def set_folder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set the folder path after receiving it from the user."""
        db_service = context.user_data["db_service"]
        llm_service = context.user_data["llm_service"]
        language = context.user_data.get("language", "English")
        folder_path = update.message.text.strip()
        user_id = context.user_data["user_id"]
        user_name = update.effective_user.full_name

        # Check if the folder path exists
        if not os.path.isdir(folder_path):
            system_response = text.Responses.invalid_folder_path(language=language)
            await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
            # Save event log
            context.user_data["system_response"] = system_response
            return ConversationHandler.END

        # Check for valid files
        valid_files_in_folder = [
            f
            for f in os.listdir(folder_path)
            if f.lower().endswith((".pdf", ".docx", ".xlsx"))
        ]
        if not valid_files_in_folder:
            system_response = text.Responses.no_valid_files(language=language)
            await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
            # Save event log
            context.user_data["system_response"] = system_response
            return ConversationHandler.END

        # Set user-specific folder path and process the documents
        context.user_data["folder_path"] = folder_path
        context.user_data["valid_files_in_folder"] = valid_files_in_folder
        context.user_data["context_source"] = "folder"  # Set context source as folder
        index_status = llm_service.load_and_index_documents(folder_path)

        # Check if indexing was successful
        if index_status != "Documents successfully indexed.":
            logging.error(f"Error during load_and_index_documents: {index_status}")
            system_response = text.Responses.indexing_error(language=language)
            await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
            # Save event log
            context.user_data["system_response"] = system_response
            return ConversationHandler.END

        context.user_data["vector_store_loaded"] = True

        # Retrieve list of empty documents
        empty_list = llm_service.get_empty_docs(folder_path)

        system_response = text.Responses.folder_is_set(
            folder_path, empty_list if empty_list else None, language=language
        )
        await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)

        # Save folder path in database
        db_service.save_folder(user_id=user_id, user_name=user_name, folder=folder_path)

        # Save event log
        context.user_data["system_response"] = system_response

        return ConversationHandler.END

    @authorized_only
    @initialize_services
    @log_event(event_type="command")
    async def clear_context(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /clear_context command."""
        language = context.user_data.get("language", "English")
        # Clear context data
        keys_to_clear = [
            "folder_path",
            "vector_store_loaded",
            "valid_files_in_folder",
            "context_source",
            "file_id_map",
            "conversation_id",
        ]
        for key in keys_to_clear:
            context.user_data.pop(key, None)

        # Clear the vector store
        llm_service = context.user_data.get("llm_service")
        if llm_service and hasattr(llm_service, "vector_store"):
            llm_service.vector_store = None

        # Optionally, remove any uploaded files from the user's upload folder
        user_id = context.user_data["user_id"]
        user_folder = f"user_documents/{user_id}"
        if os.path.exists(user_folder):
            for filename in os.listdir(user_folder):
                file_path = os.path.join(user_folder, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            # Remove the user folder if empty
            if not os.listdir(user_folder):
                os.rmdir(user_folder)

        # Optionally, clear the last folder path from the database
        db_service = context.user_data["db_service"]
        db_service.clear_user_folder(user_id)

        system_response = text.Responses.context_cleared(language=language)
        await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)

        # Save event log
        context.user_data["system_response"] = system_response

    @authorized_only
    @initialize_services
    @ensure_documents_indexed
    @log_event(event_type="ai_conversation")
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle any text message sent by the user."""

        db_service = context.user_data["db_service"]
        llm_service = context.user_data["llm_service"]
        user_message = update.message.text
        user_id = context.user_data["user_id"]
        language = context.user_data.get("language", "English")
        # Generate conversation_id and store it in context.user_data
        conversation_id = str(uuid.uuid4())
        context.user_data["conversation_id"] = conversation_id

        # Save the user's message
        db_service.save_message(conversation_id, "user", user_id, user_message)

        # Retrieve chat history
        chat_history_texts = db_service.get_chat_history(CHAT_HISTORY_LEVEL, user_id)
        chat_history = messages_to_langchain_messages(chat_history_texts)

        try:
            response, source_files = llm_service.generate_response(
                user_message, chat_history=chat_history
            )
        except Exception as e:
            logging.error(f"Error during generate_response: {e}")
            system_response = text.Responses.processing_error(language=language)
            await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
            # Save event log
            context.user_data["system_response"] = system_response
            return ConversationHandler.END

        # Prepare the bot's response
        bot_message = f"{response}"

        if source_files:
            # Create a mapping from short IDs to filenames
            file_id_map = {}
            keyboard = []
            for idx, file in enumerate(source_files):
                # Generate a short ID, e.g., 'file_0', 'file_1', etc.
                file_id = f"file_{idx}"
                file_id_map[file_id] = file
                keyboard.append(
                    [InlineKeyboardButton(file, callback_data=f"get_file:{file_id}")]
                )

            # Store the mapping in context.user_data
            context.user_data["file_id_map"] = file_id_map

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(bot_message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(response, parse_mode=ParseMode.HTML)

        # Save the bot's message
        db_service.save_message(conversation_id, "bot", None, bot_message)

        context.user_data["system_response"] = bot_message

    @authorized_only
    @initialize_services
    async def handle_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle file uploads from the user. Each upload replaces the previous context."""

        try:
            user = update.message.from_user
            user_id = user.id
            user_folder = f"user_documents/{user_id}"
            db_service = context.user_data["db_service"]
            llm_service = context.user_data["llm_service"]
            language = context.user_data.get("language", "English")
            # Create the user directory if it doesn't exist
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
            else:
                # Optionally clear existing files in the user folder
                # For now, we keep existing files
                pass

            message = update.message
            documents = [message.document] if message.document else message.documents

            if not documents:
                system_response = text.Responses.no_files_received(language=language)
                await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
                return

            valid_files = []
            invalid_files = []

            for doc in documents:
                if doc.mime_type in [
                    "application/pdf",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ]:
                    if doc.file_size > 20 * 1024 * 1024:
                        system_response = text.Responses.file_too_large()
                        await update.message.reply_text(system_response)
                        return
                    valid_files.append(doc)
                    # Download the file
                    file = await context.bot.get_file(doc.file_id)
                    file_name = os.path.basename(doc.file_name)
                    file_path = os.path.join(user_folder, file_name)
                    await file.download_to_drive(custom_path=file_path)
                else:
                    invalid_files.append(doc)

            if valid_files:
                # Update context with folder path and valid files
                context.user_data["folder_path"] = user_folder
                context.user_data["context_source"] = (
                    "upload"  # Set context source as upload
                )
                valid_files_in_folder = [
                    f
                    for f in os.listdir(user_folder)
                    if f.lower().endswith((".pdf", ".docx", ".xlsx"))
                ]
                context.user_data["valid_files_in_folder"] = valid_files_in_folder

                # Index documents
                index_status = llm_service.load_and_index_documents(user_folder)
                if index_status != "Documents successfully indexed.":
                    logging.error(
                        f"Error during load_and_index_documents: {index_status}"
                    )
                    system_response = text.Responses.indexing_error(language=language)
                    await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
                    return
                context.user_data["vector_store_loaded"] = True

                # Save folder path in database
                user_name = update.effective_user.full_name
                db_service.save_folder(
                    user_id=user_id, user_name=user_name, folder=user_folder
                )

                # Generate appropriate messages
                if not invalid_files:
                    system_response = text.Responses.upload_success(language=language)
                else:
                    system_response = text.Responses.upload_partial_success(language=language)
                await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
            else:
                if invalid_files and not valid_files:
                    system_response = text.Responses.unsupported_files(language=language)
                else:
                    system_response = text.Responses.processing_error(language=language)
                await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)

            # Save event log
            context.user_data["system_response"] = system_response

        except Exception as e:
            # Log the error
            logging.error(f"Error handling file: {e}")
            system_response = text.Responses.generic_error(language=language)
            await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)

    @authorized_only
    @initialize_services
    @log_event(event_type="inline_button")
    async def send_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        language = context.user_data.get("language", "English")

        # Immediately answer the callback to prevent timeout
        await query.answer()
        data = query.data

        if data.startswith("get_file:"):
            file_id = data[len("get_file:"):]
            file_id_map = context.user_data.get("file_id_map", {})
            file_name = file_id_map.get(file_id)

            if not file_name:
                system_response = text.FileResponses.file_not_found()
                await query.message.reply_text(system_response)
                context.user_data["system_response"] = system_response
                return

            folder_path = context.user_data.get("folder_path")
            if not folder_path:
                system_response = text.FileResponses.folder_not_set()
                await query.message.reply_text(system_response)
                context.user_data["system_response"] = system_response
                return

            file_path = os.path.join(folder_path, file_name)
            if not os.path.isfile(file_path):
                system_response = text.FileResponses.file_not_found()
                await query.message.reply_text(system_response)
                context.user_data["system_response"] = system_response
                return

            # Offload the file sending to a background task
            asyncio.create_task(
                self.send_document_async(query, file_path, file_name, language, context)
            )
        else:
            system_response = text.Responses.unknown_command(language=language)
            await query.message.reply_text(system_response)
            context.user_data["system_response"] = system_response

    async def send_document_async(self, query, file_path, file_name, language, context):
        try:
            async with aiofiles.open(file_path, "rb") as f:
                file_data = await f.read()

            await query.message.reply_document(
                document=file_data,
                filename=file_name
            )
            context.user_data["system_response"] = None  # File sent successfully
            logging.info(f"File '{file_name}' sent successfully to user {query.from_user.id}.")
        except Exception as e:
            logging.error(f"Error sending file '{file_name}' to user {query.from_user.id}: {e}")
            system_response = text.FileResponses.send_file_error()
            await query.message.reply_text(system_response)
            context.user_data["system_response"] = system_response

    @log_event(event_type="command")
    async def request_access(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_id = user.id
        user_name = user.full_name
        username = user.username
        language_code = user.language_code
        language = context.user_data.get("language", "English")

        # Initialize db_service in context if not already present
        if "db_service" not in context.user_data:
            context.user_data["db_service"] = DatabaseService()

        # Save or update user info
        db_service = context.user_data["db_service"]
        db_service.save_user_info(user_id, user_name, language_code)

        # Send a notification to the admin
        admin_id = os.getenv("ADMIN_TELEGRAM_ID")
        message = f"Access request from {user_name} (@{username}), ID: {user_id}"
        await context.bot.send_message(chat_id=admin_id, text=message, parse_mode=ParseMode.HTML)

        # Inform the user
        system_response = text.Responses.access_requested(language=language)
        await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
        context.user_data["system_response"] = system_response

    @authorized_only
    @initialize_services
    async def grant_access(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        language = context.user_data.get("language", "English")
        admin_id = update.effective_user.id
        if str(admin_id) != os.getenv("ADMIN_TELEGRAM_ID"):
            await update.message.reply_text(text.Responses.unauthorized_action(language=language), parse_mode=ParseMode.HTML)
            return

        try:
            user_id_to_grant = int(context.args[0])
            db_service = context.user_data["db_service"]
            db_service.grant_access(user_id_to_grant)
            system_response = text.Responses.grant_access_success(user_id_to_grant, language=language)
            await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
        except (IndexError, ValueError):
            system_response = text.Responses.grant_access_usage(language=language)
            await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
