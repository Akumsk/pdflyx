# logging_config.py

import logging
from logging.handlers import TimedRotatingFileHandler
import os


def setup_logging(
        log_directory='logs',
        log_file_base='bot.log',
        when='midnight',
        interval=1,
        backup_count=30,
        console_log_level=logging.INFO,
        file_log_level=logging.DEBUG,
):
    """
    Sets up logging with a TimedRotatingFileHandler and a console handler.

    Parameters:
        log_directory (str): Directory where log files will be stored.
        log_file_base (str): Base name of the log file.
        when (str): Specifies the type of interval (e.g., 'midnight' for daily rotation).
        interval (int): The interval at which to rotate logs.
        backup_count (int): Number of backup files to keep.
        console_log_level (int): Logging level for the console handler.
        file_log_level (int): Logging level for the file handler.
    """
    # Ensure the log directory exists
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Create the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels; handlers will filter appropriately

    # Define the log file path
    log_file_path = os.path.join(log_directory, log_file_base)

    # Create a formatter that includes timestamp, logger name, log level, and message
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Setup TimedRotatingFileHandler
    file_handler = TimedRotatingFileHandler(
        filename=log_file_path,
        when=when,
        interval=interval,
        backupCount=backup_count,
        encoding='utf-8',
        delay=False,
        utc=False  # Set to True if you want UTC time; False for local time
    )
    file_handler.setLevel(file_log_level)
    file_handler.setFormatter(formatter)
    file_handler.suffix = "%Y-%m-%d"  # Append date to log file name

    # Prevent duplicate log entries if multiple handlers are added
    if not any(isinstance(handler, TimedRotatingFileHandler) for handler in logger.handlers):
        logger.addHandler(file_handler)

    # Setup console handler for real-time feedback
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optionally, reduce verbosity for specific libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

    logger.debug("Logging has been configured successfully.")

