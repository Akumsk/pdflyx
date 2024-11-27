#decorators.py

import logging
import uuid
from functools import wraps

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

import text
from db_service import DatabaseService

logger = logging.getLogger(__name__)

def log_errors(default_return=None):
    """
    Decorator to log exceptions in functions or methods.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"Entering function: {func.__name__} with args: {args}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Exiting function: {func.__name__} with result: {result}")
                return result
            except Exception as e:
                logger.exception(f"Exception occurred in {func.__name__}: {str(e)}")
                if default_return is not None:
                    return default_return
                else:
                    raise
        return wrapper
    return decorator

def log_errors_async(default_return=None):
    """
    Asynchronous decorator to log exceptions in async functions or methods.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger.debug(f"Entering async function: {func.__name__} with args: {args}, kwargs: {kwargs}")
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"Exiting async function: {func.__name__} with result: {result}")
                return result
            except Exception as e:
                logger.exception(f"Exception occurred in {func.__name__}: {str(e)}")
                if default_return is not None:
                    return default_return
                else:
                    raise
        return wrapper
    return decorator


def log_event(event_type):
    """
    Decorator to log specific events with a given event type.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            user_message = update.message.text if update.message else (
                update.callback_query.data if update.callback_query else ""
            )
            conversation_id = context.user_data.get("conversation_id", str(uuid.uuid4()))
            context.user_data.setdefault("conversation_id", conversation_id)
            system_response = context.user_data.get("system_response", "")

            logger.info(f"Event '{event_type}' triggered by user_id={user_id}, message='{user_message}'")

            try:
                result = await func(self, update, context, *args, **kwargs)
                system_response = context.user_data.get("system_response", system_response)
            except Exception as e:
                logger.exception(f"Exception in handler function {func.__name__}: {e}")
                language = context.user_data.get("language", "English")
                system_response = text.Responses.generic_error(language=language)
                try:
                    if update.message:
                        await update.message.reply_text(system_response, parse_mode=ParseMode.HTML)
                    elif update.callback_query:
                        await update.callback_query.message.reply_text(system_response, parse_mode=ParseMode.HTML)
                except Exception as reply_exception:
                    logger.exception(f"Failed to send error message to user_id {user_id}: {reply_exception}")
                context.user_data["system_response"] = system_response
                result = None

            # Save event log to the database
            db_service = context.user_data.get("db_service")
            if db_service:
                try:
                    db_service.save_event_log(
                        user_id=user_id,
                        event_type=event_type,
                        user_message=user_message,
                        system_response=system_response,
                        conversation_id=conversation_id,
                    )
                    logger.debug(f"Event log saved for user_id={user_id}, event_type={event_type}")
                except Exception as e:
                    logger.exception(f"Failed to save event log for user_id {user_id}: {e}")
            else:
                logger.error("db_service not found in context.user_data")

            return result
        return wrapper
    return decorator


def authorized_only(func):
    """
    Decorator to ensure that only authorized users can access the handler.
    """
    @wraps(func)
    async def wrapper(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user = update.effective_user
        user_id = user.id
        user_name = user.full_name
        language_code = user.language_code

        if "db_service" not in context.user_data:
            context.user_data["db_service"] = DatabaseService()
            logger.debug(f"Initialized DatabaseService for user_id={user_id}")

        db_service = context.user_data["db_service"]

        try:
            # Save or update user info
            db_service.save_user_info(user_id, user_name, language_code)
            logger.debug(f"User info saved for user_id={user_id}")
        except Exception as e:
            logger.exception(f"Failed to save user info for user_id {user_id}: {e}")
            system_response = text.Responses.generic_error(language="English")
            if update.message:
                await update.message.reply_text(system_response)
            elif update.callback_query:
                await update.callback_query.answer(
                    system_response,
                    show_alert=True,
                )
            return

        try:
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
                logger.info(f"Access denied for user_id={user_id}")
                return
            else:
                # Update last_active
                db_service.update_last_active(user_id)
                logger.debug(f"Updated last_active for user_id={user_id}")
        except Exception as e:
            logger.exception(f"Error checking/updating access for user_id {user_id}: {e}")
            system_response = text.Responses.generic_error(language="English")
            if update.message:
                await update.message.reply_text(system_response)
            elif update.callback_query:
                await update.callback_query.answer(
                    system_response,
                    show_alert=True,
                )
            return

        return await func(self, update, context, *args, **kwargs)

    return wrapper


def initialize_services(func):
    """
    Decorator to initialize necessary services before handling the request.
    """
    @wraps(func)
    async def wrapper(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        try:
            from llm_service import LLMService  # Deferred import

            if "db_service" not in context.user_data:
                context.user_data["db_service"] = DatabaseService()
                logger.debug("Initialized DatabaseService.")
            if "llm_service" not in context.user_data:
                context.user_data["llm_service"] = LLMService()
                logger.debug("Initialized LLMService.")
            if "user_id" not in context.user_data:
                context.user_data["user_id"] = update.effective_user.id
                logger.debug(f"Set user_id: {context.user_data['user_id']}")
            if "user_name" not in context.user_data:
                context.user_data["user_name"] = update.effective_user.full_name
                logger.debug(f"Set user_name: {context.user_data['user_name']}")
            if "language_code" not in context.user_data:
                context.user_data["language_code"] = update.effective_user.language_code
                logger.debug(f"Set language_code: {context.user_data['language_code']}")

            # Access db_service
            db_service = context.user_data["db_service"]
            user_id = context.user_data["user_id"]

            # Fetch current_language from the database
            current_language = db_service.get_current_language(user_id)
            if current_language:
                context.user_data["language"] = current_language
                logger.debug(f"Fetched current_language for user_id={user_id}: {current_language}")
            else:
                # If current_language is not set, initialize it with language_code
                language_code = context.user_data["language_code"]
                context.user_data["language"] = language_code
                db_service.update_current_language(user_id, language_code)
                logger.debug(f"Initialized language for user_id={user_id}: {language_code}")
        except Exception as e:
            logger.exception(f"Error initializing services for user_id {context.user_data.get('user_id')}: {e}")
            system_response = text.Responses.generic_error(language="English")
            if update.message:
                await update.message.reply_text(system_response)
            elif update.callback_query:
                await update.callback_query.answer(
                    system_response,
                    show_alert=True,
                )
            return

        return await func(self, update, context, *args, **kwargs)

    return wrapper


def ensure_documents_indexed(func):
    """
    Decorator to ensure that documents are indexed before proceeding.
    """
    @wraps(func)
    async def wrapper(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        language = context.user_data.get("language", "English")
        try:
            if not context.user_data.get("vector_store_loaded", False):
                system_response = text.ContextErrors.documents_not_indexed(language=language)
                await update.message.reply_text(system_response)
                logger.warning(f"Documents not indexed for user_id={context.user_data.get('user_id')}")
                return ConversationHandler.END
            valid_files_in_folder = context.user_data.get("valid_files_in_folder", [])
            if not valid_files_in_folder:
                system_response = text.ContextErrors.no_valid_documents(language=language)
                await update.message.reply_text(system_response)
                logger.warning(f"No valid documents found for user_id={context.user_data.get('user_id')}")
                return ConversationHandler.END
        except Exception as e:
            logger.exception(f"Error ensuring documents are indexed for user_id {context.user_data.get('user_id')}: {e}")
            system_response = text.Responses.generic_error(language=context.user_data.get("language", "English"))
            await update.message.reply_text(system_response)
            return ConversationHandler.END

        return await func(self, update, context, *args, **kwargs)

    return wrapper
