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

import logging_config


def main():
    # Setup logging
    logging_config.setup_logging(
        log_directory='logs',
        log_file_base='bot.log',
        when='midnight',
        interval=1,
        backup_count=30,
        console_log_level=logging.INFO,
        file_log_level=logging.DEBUG,
        max_log_length=1000,  # Adjust as needed
    )

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
    application.add_handler(CommandHandler("references", handlers.references_command))

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
    application.add_handler(
        CallbackQueryHandler(handlers.handle_inline_buttons)
    )

    # Message Handlers
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message)
    )

    application.run_polling()


if __name__ == "__main__":
    main()
