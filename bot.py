# bot.py

import logging
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
    WAITING_FOR_FOLDER_PATH,
    WAITING_FOR_QUESTION,
    WAITING_FOR_PROJECT_SELECTION,
)
from exception_handlers import (
    error_handler,
    handle_telegram_context_length_exceeded_error,
)


def main():
    logging.basicConfig(level=logging.INFO)

    handlers = BotHandlers()

    application = (
        ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(handlers.post_init).build()
    )

    folder_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("folder", handlers.folder),
            CommandHandler("start", handlers.start),
        ],
        states={
            WAITING_FOR_FOLDER_PATH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.set_folder)
            ],
        },
        fallbacks=[],
    )


    application.add_handler(CommandHandler("status", handlers.status))
    application.add_handler(folder_conv_handler)

    # Handler for file download
    application.add_handler(CallbackQueryHandler(handlers.send_file, pattern=r'^get_file:'))

    # Handlers for access control
    application.add_handler(CommandHandler("request_access", handlers.request_access))
    application.add_handler(CommandHandler("grant_access", handlers.grant_access))

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message)
    )

    application.add_error_handler(error_handler)

    application.run_polling()


if __name__ == "__main__":
    main()