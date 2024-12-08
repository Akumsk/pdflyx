# handlers.py

import logging
import os
import uuid
import asyncio

import aiofiles
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)
from telegram.constants import ParseMode

from llm_service import LLMService
from settings import CHAT_HISTORY_LEVEL, knowledge_base_paths, SUPPORTED_LANGUAGES, knowledge_base_language
from db_service import DatabaseService
from decorators import log_errors, log_event, authorized_only, initialize_services, ensure_documents_indexed
from helpers import messages_to_langchain_messages, get_language_code, get_language_name
import text
from text import KnowledgeBaseResponses, CommandDescriptions

logger = logging.getLogger(__name__)

WAITING_FOR_FOLDER_PATH = range(1)

class BotHandlers:
    def __init__(self):
        pass

    def initialize_database_service(self):
        try:
            db_service = DatabaseService()
            return db_service
        except Exception as e:
            logger.error(f"Failed to initialize DatabaseService: {e}")
            return None

    def initialize_llm_service(self):
        try:
            llm_service = LLMService()
            return llm_service
        except Exception as e:
            logger.error(f"Failed to initialize LLMService: {e}")
            return None

    async def post_init(self, application):
        """
        Initializes bot commands with multilingual support.
        """
        for language in SUPPORTED_LANGUAGES:
            commands = text.CommandDescriptions.get_commands(language=language)
            language_code = get_language_code(language)
            try:
                await application.bot.set_my_commands(
                    commands,
                    language_code=language_code
                )
                logger.info(f"Commands set for language: {language} ({language_code})")
            except Exception as e:
                logger.exception(f"Failed to set commands for {language} ({language_code}): {e}")

    async def global_error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """
        Global error handler to catch and log all exceptions.
        """
        logger.error("Exception while handling an update:", exc_info=context.error)

        # Optionally, notify administrators or take corrective actions
        if isinstance(update, Update) and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "An unexpected error occurred. Please try again later."
                )
            except Exception as e:
                logger.error(f"Failed to send error message to user: {e}")


    @initialize_services
    @log_event(event_type="command")
    @log_errors(default_return=None)
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not user:
            logger.error("No effective user found in the update.")
            await update.message.reply_text("An error occurred. Please try again.")
            return

        user_id = user.id
        user_name = user.first_name or "there"
        language_code = user.language_code or "en"

        # Debug log
        logger.debug(f"User ID: {user_id}, User Name: {user_name}, Language Code: {language_code}")

        # Initialize DatabaseService from bot_data
        db_service: DatabaseService = context.bot_data.get("db_service")
        if not db_service:
            logger.error("DatabaseService not found in bot_data.")
            await update.message.reply_text("An internal error occurred. Please try again later.")
            return

        # Save or update user info in the database
        try:
            db_service.save_user_info(user_id, user_name, language_code)
            logger.info(f"User info saved for user_id={user_id}")
        except Exception as e:
            logger.exception(f"Failed to save user info for user_id={user_id}: {e}")
            await update.message.reply_text("Failed to initialize your settings. Please try again later.")
            return

        # Determine language name based on language_code
        current_language = get_language_name(language_code)
        context.user_data["language"] = current_language
        context.user_data["user_id"] = user_id
        context.user_data["user_name"] = user_name
        context.user_data["language_code"] = language_code

        # Generate the welcome message in the user's language
        try:
            system_response = text.Greetings.first_time(language=current_language, user_name=user_name)
        except Exception as e:
            logger.exception(f"Failed to generate welcome message: {e}")
            system_response = "Welcome! (Default message)"

        await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)

        # Store system_response in context.user_data
        context.user_data["system_response"] = system_response
        logger.info(f"Sent welcome message to user_id={user_id}")

    @authorized_only
    @initialize_services
    @log_event(event_type="command")
    @log_errors(default_return=None)
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
        logger.info(f"Prompted language selection for user_id={context.user_data['user_id']}")

    @authorized_only
    @initialize_services
    @log_event(event_type="inline_button")
    @log_errors(default_return=None)
    async def set_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set the user's preferred language."""
        query = update.callback_query
        await query.answer()
        data = query.data
        user_id = update.effective_user.id

        if data.startswith("set_language:"):
            selected_language = data[len("set_language:"):]
            context.user_data["language"] = selected_language
            user_id = update.effective_user.id

            # Access the db_service from context.user_data
            db_service = context.user_data.get("db_service")
            if db_service:
                # Update the current_language in the database
                try:
                    db_service.update_current_language(user_id, selected_language)
                    logger.debug(f"Updated language to '{selected_language}' for user_id={user_id}")
                except Exception as e:
                    logger.exception(f"Failed to update language for user_id {user_id}: {e}")
            else:
                logger.error("db_service not found in context.user_data")

            # Use language-specific response
            system_response = text.LanguageResponses.language_set_success(selected_language)
            await query.message.reply_text(system_response)
            context.user_data["system_response"] = system_response
            logger.info(f"User_id={user_id} set language to '{selected_language}'")
        else:
            system_response = text.Responses.unknown_command(language=context.user_data.get("language", "English"))
            await query.message.reply_text(system_response)
            context.user_data["system_response"] = system_response
            logger.warning(f"Unknown language command received from user_id={user_id}")

    @authorized_only
    @initialize_services
    @log_event(event_type="command")
    @log_errors(default_return=None)
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
        context.user_data["system_response"] = system_response
        logger.info(f"Provided status to user_id={context.user_data['user_id']}")

    @authorized_only
    @initialize_services
    @log_event(event_type="command")
    @log_errors(default_return=None)
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
        context.user_data["system_response"] = system_response
        logger.info(f"Prompted knowledge base selection for user_id={context.user_data['user_id']}")

    @authorized_only
    @initialize_services
    @log_event(event_type="inline_button")
    @log_errors(default_return=None)
    async def set_knowledge_base(
            self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Handler to set the folder path based on the user's knowledge base selection.
        """
        query = update.callback_query
        language = context.user_data.get("language", "English")
        await query.answer()
        data = query.data
        user_id = context.user_data["user_id"]

        if data.startswith("set_knowledge:"):
            selection = data[len("set_knowledge:"):]
            folder_path = knowledge_base_paths.get(selection, None)
            knowledge_base_lang = knowledge_base_language.get(selection, 'English')  # Get the knowledge base language
            if folder_path is None:
                system_response = KnowledgeBaseResponses.unknown_knowledge_base()
                await query.message.reply_text(system_response)
                context.user_data["system_response"] = system_response
                logger.warning(f"Unknown knowledge base selection '{selection}' by user_id={user_id}")
                return

            # Set the folder path and process the documents
            context.user_data["folder_path"] = folder_path
            context.user_data["context_source"] = "folder"  # Set context source as folder
            logger.debug(f"Set folder_path='{folder_path}' for user_id={user_id}")

            # Index the documents in the folder
            llm_service = context.user_data["llm_service"]
            try:
                valid_files_in_folder = [
                    f
                    for f in os.listdir(folder_path)
                    if f.lower().endswith((".pdf", ".docx", ".xlsx"))
                ]
                context.user_data["valid_files_in_folder"] = valid_files_in_folder
                logger.debug(f"Found {len(valid_files_in_folder)} valid files in folder_path='{folder_path}' for user_id={user_id}")

                if not valid_files_in_folder:
                    await query.message.reply_text(
                        KnowledgeBaseResponses.no_valid_files_in_knowledge_base(language=language),
                        parse_mode=ParseMode.HTML
                    )
                    logger.warning(f"No valid files in knowledge base '{selection}' for user_id={user_id}")
                    return

                # Pass the knowledge base language to load_and_index_documents
                index_status, index_message = llm_service.load_and_index_documents(folder_path, knowledge_base_lang)
                if not index_status:
                    logger.error(f"Error during load_and_index_documents: {index_message}")
                    await query.message.reply_text(KnowledgeBaseResponses.indexing_error(language=language),
                                                   parse_mode=ParseMode.HTML)
                    return

                context.user_data["vector_store_loaded"] = True
                system_response = KnowledgeBaseResponses.knowledge_base_set_success(selection, language=language)
                await query.message.reply_text(system_response, parse_mode=ParseMode.HTML)
                context.user_data["system_response"] = system_response
                logger.info(f"Knowledge base '{selection}' set successfully for user_id={user_id}")
            except Exception as e:
                logger.exception(f"Error setting knowledge base for user_id={user_id}: {e}")
                system_response = text.Responses.generic_error(language=language)
                await query.message.reply_text(system_response, parse_mode=ParseMode.HTML)
                context.user_data["system_response"] = system_response
        else:
            system_response = KnowledgeBaseResponses.unknown_command(language=language)
            await query.message.reply_text(system_response, parse_mode=ParseMode.HTML)
            context.user_data["system_response"] = system_response
            logger.warning(f"Unknown knowledge base command received from user_id={user_id}")

    @authorized_only
    @initialize_services
    @log_event(event_type="command")
    @log_errors(default_return=None)
    async def set_folder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set the folder path after receiving it from the user."""
        db_service = context.user_data["db_service"]
        llm_service = context.user_data["llm_service"]
        language = context.user_data.get("language", "English")
        folder_path = update.message.text.strip()
        user_id = context.user_data["user_id"]
        user_name = context.user_data["user_name"]

        # Check if the folder path exists
        if not os.path.isdir(folder_path):
            system_response = text.Responses.invalid_folder_path(language=language)
            await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
            # Save event log
            context.user_data["system_response"] = system_response
            logger.warning(f"Invalid folder path '{folder_path}' provided by user_id={user_id}")
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
            logger.warning(f"No valid files found in folder_path='{folder_path}' for user_id={user_id}")
            return ConversationHandler.END

        # Set user-specific folder path and process the documents
        context.user_data["folder_path"] = folder_path
        context.user_data["valid_files_in_folder"] = valid_files_in_folder
        context.user_data["context_source"] = "folder"  # Set context source as folder
        logger.debug(f"Set folder_path='{folder_path}' for user_id={user_id}")

        try:
            # For custom folders, you might not have a predefined language.
            # You can set a default language or prompt the user to specify.
            # Here, we'll set the default language to 'English'.
            knowledge_base_lang = 'English'  # Default language
            index_status, index_message = llm_service.load_and_index_documents(folder_path, knowledge_base_lang)
            if not index_status:
                logger.error(f"Error during load_and_index_documents: {index_message}")
                system_response = text.Responses.indexing_error(language=language)
                await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
                # Save event log
                context.user_data["system_response"] = system_response
                return ConversationHandler.END

            context.user_data["vector_store_loaded"] = True
            logger.info(f"Documents indexed successfully for folder_path='{folder_path}' by user_id={user_id}")

            # Retrieve list of empty documents
            empty_list = llm_service.get_empty_docs(folder_path)

            system_response = text.Responses.folder_is_set(
                folder_path, empty_list if empty_list else None, language=language
            )
            await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)

            # Save folder path in database
            db_service.save_folder(user_id=user_id, user_name=user_name, folder=folder_path)
            logger.debug(f"Folder path '{folder_path}' saved in database for user_id={user_id}")

            # Save event log
            context.user_data["system_response"] = system_response
        except Exception as e:
            logger.exception(f"Error setting folder for user_id={user_id}: {e}")
            system_response = text.Responses.generic_error(language=language)
            await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
            context.user_data["system_response"] = system_response
            return ConversationHandler.END

        return ConversationHandler.END

    @authorized_only
    @initialize_services
    @log_event(event_type="command")
    @log_errors(default_return=None)
    async def clear_context(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /clear_context command."""
        language = context.user_data.get("language", "English")
        user_id = context.user_data["user_id"]
        logger.info(f"User_id={user_id} initiated /clear_context command.")

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
            logger.debug(f"Cleared context key '{key}' for user_id={user_id}")

        # Clear the vector store
        llm_service = context.user_data.get("llm_service")
        if llm_service and hasattr(llm_service, "vector_store"):
            llm_service.vector_store = None
            logger.debug(f"Cleared vector_store for user_id={user_id}")

        # Optionally, remove any uploaded files from the user's upload folder
        user_id = context.user_data["user_id"]
        user_folder = f"user_documents/{user_id}"
        if os.path.exists(user_folder):
            try:
                for filename in os.listdir(user_folder):
                    file_path = os.path.join(user_folder, filename)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        logger.debug(f"Deleted file '{file_path}' for user_id={user_id}")
                # Remove the user folder if empty
                if not os.listdir(user_folder):
                    os.rmdir(user_folder)
                    logger.debug(f"Removed empty folder '{user_folder}' for user_id={user_id}")
            except Exception as e:
                logger.exception(f"Error cleaning up user_folder='{user_folder}' for user_id={user_id}: {e}")

        # Optionally, clear the last folder path from the database
        db_service = context.user_data["db_service"]
        try:
            db_service.clear_user_folder(user_id)
            logger.debug(f"Cleared folder path in database for user_id={user_id}")
        except Exception as e:
            logger.exception(f"Failed to clear folder path in database for user_id={user_id}: {e}")

        system_response = text.Responses.context_cleared(language=language)
        await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)

        # Save event log
        context.user_data["system_response"] = system_response
        logger.info(f"Context cleared for user_id={user_id}")

    @authorized_only
    @initialize_services
    @log_event(event_type="command")
    @log_errors(default_return=None)
    async def references_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /references command."""
        language = context.user_data.get("language", "English")
        user_id = update.effective_user.id
        source_files = context.user_data.get("source_files", [])

        if not source_files:
            system_response = "No references available."
            await update.message.reply_text(system_response)
            context.user_data["system_response"] = system_response
            logger.info(f"No references available for user_id={user_id}")
            return

        # Send message "Please select reference for downloading below"
        system_response = "Please select reference for downloading below"
        keyboard = []
        file_id_map = {}
        for idx, file in enumerate(source_files):
            file_id = f"file_{idx}"
            file_id_map[file_id] = file
            keyboard.append(
                [InlineKeyboardButton(file, callback_data=f"get_file:{file_id}")]
            )
        context.user_data["file_id_map"] = file_id_map
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(system_response, reply_markup=reply_markup)
        context.user_data["system_response"] = system_response
        logger.info(f"Sent reference buttons to user_id={user_id}")

    async def _process_user_message(self, user_message, update, context, prepend_user_message=False):
        """Process a user message and generate a response."""
        db_service = context.user_data["db_service"]
        llm_service = context.user_data["llm_service"]
        user_id = context.user_data["user_id"]
        language = context.user_data.get("language", "English")

        # Generate conversation_id and store it in context.user_data
        conversation_id = str(uuid.uuid4())
        context.user_data["conversation_id"] = conversation_id
        logger.debug(f"Generated conversation_id='{conversation_id}' for user_id={user_id}")

        # Save the user's message
        try:
            db_service.save_message(conversation_id, "user", user_id, user_message)
            logger.debug(f"Saved user message for conversation_id='{conversation_id}'")
        except Exception as e:
            logger.exception(f"Failed to save user message for conversation_id='{conversation_id}': {e}")

        # Retrieve chat history
        try:
            chat_history_texts = db_service.get_chat_history(CHAT_HISTORY_LEVEL, user_id)
            chat_history = messages_to_langchain_messages(chat_history_texts)
            logger.debug(f"Retrieved chat history for user_id={user_id}")
        except Exception as e:
            logger.exception(f"Failed to retrieve chat history for user_id={user_id}: {e}")
            system_response = text.Responses.generic_error(language=language)
            await update.effective_message.reply_text(system_response, parse_mode=ParseMode.HTML)
            context.user_data["system_response"] = system_response
            return ConversationHandler.END

        try:
            # Generate response using LLM service
            response, source_files, suggestions = llm_service.generate_response(
                user_message, chat_history=chat_history
            )
            logger.info(f"Generated response for user_id={user_id}")
        except Exception as e:
            logger.exception(f"Error during generate_response for user_id {user_id}: {e}")
            system_response = text.Responses.processing_error(language=language)
            await update.effective_message.reply_text(system_response, parse_mode=ParseMode.HTML)
            context.user_data["system_response"] = system_response
            return ConversationHandler.END

        # Prepare the bot's message
        if prepend_user_message:
            bot_message = f"{user_message}\n-----------\n{response}"
        else:
            bot_message = response

        # Save the bot's message
        try:
            db_service.save_message(conversation_id, "bot", None, bot_message)
            logger.debug(f"Saved bot message for conversation_id='{conversation_id}'")
        except Exception as e:
            logger.exception(f"Failed to save bot message for conversation_id='{conversation_id}': {e}")

        # Store the system response in context
        context.user_data["system_response"] = bot_message

        # Update source_files if new references are provided
        if source_files:
            context.user_data["source_files"] = source_files  # Replace with new references
        else:
            # Do not update source_files if no new references are provided
            context.user_data["source_files"] = []  # Clear references

        try:
            # Send the response with HTML parsing
            keyboard = []
            if suggestions:
                # Prepare suggestion buttons
                suggestion_id_map = {}
                for idx, suggestion in enumerate(suggestions):
                    suggestion_id = f"suggestion_{idx}"
                    suggestion_id_map[suggestion_id] = suggestion
                    keyboard.append(
                        [InlineKeyboardButton(suggestion, callback_data=f"suggestion:{suggestion_id}")]
                    )
                context.user_data["suggestion_id_map"] = suggestion_id_map
                logger.info(f"Prepared suggestion buttons for user_id={user_id}")

            if keyboard:
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.effective_message.reply_text(bot_message, reply_markup=reply_markup,
                                                          parse_mode=ParseMode.HTML)
                logger.info(f"Sent response with inline buttons to user_id={user_id}")
            else:
                # Send bot message without inline buttons
                await update.effective_message.reply_text(bot_message, parse_mode=ParseMode.HTML)
                logger.info(f"Sent response to user_id={user_id}")

        except Exception as e:
            # If it fails, send without parse mode
            logger.warning(f"Failed to send message with HTML parse mode for user_id {user_id}: {e}")
            await update.effective_message.reply_text(bot_message)
            logger.info(f"Sent response without parse mode to user_id={user_id}")


    @authorized_only
    @initialize_services
    @ensure_documents_indexed
    @log_event(event_type="ai_conversation")
    @log_errors(default_return=None)
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle any text message sent by the user."""
        user_message = update.message.text
        await self._process_user_message(user_message, update, context)

    @authorized_only
    @initialize_services
    @log_event(event_type="inline_button")
    @log_errors(default_return=None)
    async def handle_inline_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks."""
        query = update.callback_query
        language = context.user_data.get("language", "English")
        user_id = update.effective_user.id

        # Immediately answer the callback to prevent timeout
        await query.answer()
        data = query.data

        if data.startswith("suggestion:"):
            suggestion_id = data[len("suggestion:"):]
            suggestion_id_map = context.user_data.get("suggestion_id_map", {})
            suggestion = suggestion_id_map.get(suggestion_id)

            if not suggestion:
                system_response = "Suggestion not found or expired."
                await query.message.reply_text(system_response)
                context.user_data["system_response"] = system_response
                logger.warning(f"Suggestion ID '{suggestion_id}' not found for user_id={user_id}")
                return

            # Log the usage of the suggestion
            logger.info(f"User_id={user_id} clicked on suggestion '{suggestion}'")

            # Call _process_user_message with the suggestion and prepend_user_message flag
            await self._process_user_message(suggestion, update, context, prepend_user_message=True)

        elif data.startswith("get_file:"):
            # ... [Handle file download] ...
            pass
        else:
            system_response = text.Responses.unknown_command(language=language)
            await query.message.reply_text(system_response)
            context.user_data["system_response"] = system_response
            logger.warning(f"Unknown callback data '{data}' received from user_id={user_id}")

    @authorized_only
    @initialize_services
    @log_event(event_type="inline_button")
    @log_errors(default_return=None)
    async def send_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        language = context.user_data.get("language", "English")
        user_id = update.effective_user.id

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
                logger.warning(f"File ID '{file_id}' not found for user_id={user_id}")
                return

            folder_path = context.user_data.get("folder_path")
            if not folder_path:
                system_response = text.FileResponses.folder_not_set()
                await query.message.reply_text(system_response)
                context.user_data["system_response"] = system_response
                logger.error(f"Folder path not set for user_id={user_id} while sending file.")
                return

            file_path = os.path.join(folder_path, file_name)
            if not os.path.isfile(file_path):
                system_response = text.FileResponses.file_not_found()
                await query.message.reply_text(system_response)
                context.user_data["system_response"] = system_response
                logger.warning(f"File '{file_path}' does not exist for user_id={user_id}")
                return

            # Check download_access before sending the file
            db_service = context.user_data["db_service"]
            has_access = db_service.get_download_access(file_path)

            if has_access:
                # Offload the file sending to a background task
                asyncio.create_task(
                    self.send_document_async(query, file_path, file_name, language, context)
                )
                logger.debug(f"Initiated async task to send file '{file_name}' to user_id={user_id}")
            else:
                # Access denied, send an appropriate message
                system_response = text.Responses.not_allowed_download(language=language)
                await query.message.reply_text(system_response)
                context.user_data["system_response"] = system_response
                logger.info(f"Download access denied for file '{file_path}' to user_id={user_id}")
        else:
            system_response = text.Responses.unknown_command(language=language)
            await query.message.reply_text(system_response)
            context.user_data["system_response"] = system_response
            logger.warning(f"Unknown callback data '{data}' received from user_id={user_id}")

    async def send_document_async(self, query, file_path, file_name, language, context):
        user_id = query.from_user.id
        try:
            async with aiofiles.open(file_path, "rb") as f:
                file_data = await f.read()

            await query.message.reply_document(
                document=file_data,
                filename=file_name
            )
            context.user_data["system_response"] = None  # File sent successfully
            logger.info(f"File '{file_name}' sent successfully to user_id={user_id}.")
        except Exception as e:
            logger.exception(f"Error sending file '{file_name}' to user_id={user_id}: {e}")
            system_response = text.FileResponses.send_file_error()
            try:
                await query.message.reply_text(system_response)
                logger.debug(f"Sent file error message to user_id={user_id}")
            except Exception as reply_exception:
                logger.exception(
                    f"Failed to send file error message to user_id {user_id}: {reply_exception}"
                )
            context.user_data["system_response"] = system_response

    @log_event(event_type="command")
    @log_errors(default_return=None)
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
            logger.debug(f"Initialized DatabaseService for user_id={user_id}")

        # Save or update user info
        db_service = context.user_data["db_service"]
        try:
            db_service.save_user_info(user_id, user_name, language_code)
            logger.debug(f"User info saved for user_id={user_id}")
        except Exception as e:
            logger.exception(f"Failed to save user info for user_id {user_id}: {e}")
            system_response = text.Responses.generic_error(language=language)
            await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
            context.user_data["system_response"] = system_response
            return

        # Send a notification to the admin
        admin_id = os.getenv("ADMIN_TELEGRAM_ID")
        if admin_id:
            message = f"Access request from {user_name} (@{username}), ID: {user_id}"
            try:
                await context.bot.send_message(chat_id=admin_id, text=message, parse_mode=ParseMode.HTML)
                logger.info(f"Access request from user_id={user_id} sent to admin_id={admin_id}.")
            except Exception as e:
                logger.exception(f"Failed to send access request to admin_id {admin_id}: {e}")
        else:
            logger.error("ADMIN_TELEGRAM_ID not set in environment variables.")

        # Inform the user
        system_response = text.Responses.access_requested(language=language)
        await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
        context.user_data["system_response"] = system_response
        logger.info(f"Informing user_id={user_id} about access request.")

    @authorized_only
    @initialize_services
    @log_errors(default_return=None)
    async def grant_access(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        language = context.user_data.get("language", "English")
        admin_id = update.effective_user.id
        expected_admin_id = os.getenv("ADMIN_TELEGRAM_ID")

        if str(admin_id) != expected_admin_id:
            await update.message.reply_text(
                text.Responses.unauthorized_action(language=language),
                parse_mode=ParseMode.HTML
            )
            logger.warning(f"Unauthorized access grant attempt by user_id={admin_id}.")
            return

        try:
            user_id_to_grant = int(context.args[0])
            logger.debug(f"Admin user_id={admin_id} attempting to grant access to user_id={user_id_to_grant}")
        except (IndexError, ValueError):
            system_response = text.Responses.grant_access_usage(language=language)
            await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
            context.user_data["system_response"] = system_response
            logger.warning(f"Admin user_id={admin_id} provided invalid grant access arguments.")
            return

        db_service = context.user_data["db_service"]
        try:
            db_service.grant_access(user_id_to_grant)
            logger.info(f"Granted access to user_id={user_id_to_grant} by admin_id={admin_id}")
            system_response = text.Responses.grant_access_success(user_id_to_grant, language=language)
            await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
            context.user_data["system_response"] = system_response
        except Exception as e:
            logger.exception(f"Failed to grant access to user_id {user_id_to_grant} by admin_id={admin_id}: {e}")
            system_response = text.Responses.generic_error(language=language)
            await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
            context.user_data["system_response"] = system_response

