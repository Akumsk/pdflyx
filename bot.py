# bot.py

import logging
import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    CallbackQueryHandler,
)
from telegram.error import BadRequest

from settings import TELEGRAM_TOKEN
from llm_service import LLMService
from db_service import DatabaseService
from handlers import (
    BotHandlers,
)
from exception_handlers import (
    error_handler,
)


def main():
    logging.basicConfig(level=logging.INFO)

    handlers = BotHandlers()

    application = (
        ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(handlers.post_init).build()
    )

    # Command Handlers
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("knowledge_base", handlers.knowledge_base))
    application.add_handler(CommandHandler("status", handlers.status))
    application.add_handler(CommandHandler("language", handlers.language))
    application.add_handler(CommandHandler("clear_context", handlers.clear_context))
    application.add_handler(CommandHandler("request_access", handlers.request_access))
    application.add_handler(CommandHandler("grant_access", handlers.grant_access))

    # Callback Query Handlers
    application.add_handler(
        CallbackQueryHandler(handlers.set_knowledge_base, pattern=r"^set_knowledge:")
    )
    application.add_handler(
        CallbackQueryHandler(handlers.send_file, pattern=r"^get_file:")
    )
    application.add_handler(
        CallbackQueryHandler(handlers.set_language, pattern=r"^set_language:")
    )

    # Message Handlers
    application.add_handler(MessageHandler(filters.Document.ALL, handlers.handle_file))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message)
    )

    # Error Handler
    application.add_error_handler(error_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
