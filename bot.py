# bot.py

import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from settings import TELEGRAM_TOKEN
from handlers import BotHandlers
import logging_config

logger = logging.getLogger(__name__)

def main():
    # 1. Setup Logging
    logging_config.setup_logging(
        log_directory='logs',
        log_file_base='bot.log',
        when='midnight',
        interval=1,
        backup_count=30,
        console_log_level=logging.INFO,
        file_log_level=logging.DEBUG,
        max_log_length=1000,
    )
    logger.info("Logging is set up.")

    # 2. Initialize BotHandlers
    handlers = BotHandlers()

    # 3. Build the Application with post_init
    application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .post_init(handlers.post_init)  # Pass the post_init function here
        .build()
    )
    logger.info("Application built with provided token.")

    # 4. Initialize Services and Store in bot_data
    # Initialize DatabaseService
    db_service = handlers.initialize_database_service()
    if db_service:
        application.bot_data["db_service"] = db_service
        logger.info("DatabaseService initialized and stored in bot_data.")
    else:
        logger.error("Failed to initialize DatabaseService.")

    # Initialize LLMService if needed
    llm_service = handlers.initialize_llm_service()
    if llm_service:
        application.bot_data["llm_service"] = llm_service
        logger.info("LLMService initialized and stored in bot_data.")
    else:
        logger.error("Failed to initialize LLMService.")

    # 5. Add Command Handlers
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("knowledge_base", handlers.knowledge_base))
    application.add_handler(CommandHandler("status", handlers.status))
    application.add_handler(CommandHandler("language", handlers.language))
    application.add_handler(CommandHandler("clear_context", handlers.clear_context))
    application.add_handler(CommandHandler("references", handlers.references_command))

    # 6. Add Callback Query Handlers
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

    # 7. Add Message Handlers
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message)
    )

    # 8. Register the Global Error Handler
    application.add_error_handler(handlers.global_error_handler)
    logger.info("Handlers added to the application.")

    # 9. Start the Bot
    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user.")
