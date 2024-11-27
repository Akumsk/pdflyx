# logging_config.py

import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pythonjsonlogger import jsonlogger


class TruncateFilter(logging.Filter):
    def __init__(self, max_length=1000):
        super().__init__()
        self.max_length = max_length

    def filter(self, record):
        """
        Truncates the log message if it exceeds the maximum length.
        Also clears record.args to prevent formatting errors.
        """
        try:
            message = record.getMessage()
            if len(message) > self.max_length:
                # Truncate the message and append a notice
                truncated_message = message[:self.max_length] + '... [TRUNCATED]'
                record.msg = truncated_message
                record.args = ()  # Clear args to prevent formatting
        except Exception as e:
            # In case of any unexpected error, log it and continue
            logging.getLogger(__name__).error(f"Error in TruncateFilter: {e}")
        return True  # Always return True to allow the log record to be processed


def setup_logging(
        log_directory='logs',
        log_file_base='bot.log',
        when='midnight',
        interval=1,
        backup_count=30,
        console_log_level=logging.INFO,
        file_log_level=logging.DEBUG,
        max_log_length=1000,  # Maximum length for log messages
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
        max_log_length (int): Maximum length of log messages before truncation.
    """
    # Ensure the log directory exists
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Create the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels; handlers will filter appropriately

    # Define the log file path
    log_file_path = os.path.join(log_directory, log_file_base)

    # Create a JSON formatter for structured logging (optional)
    json_formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
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
    file_handler.setFormatter(json_formatter)
    file_handler.suffix = "%Y-%m-%d"  # Append date to log file name

    # Add TruncateFilter to file handler
    truncate_filter = TruncateFilter(max_length=max_log_length)
    file_handler.addFilter(truncate_filter)

    # Prevent duplicate log entries if multiple handlers are added
    if not any(isinstance(handler, TimedRotatingFileHandler) for handler in logger.handlers):
        logger.addHandler(file_handler)

    # Setup console handler with a simple formatter
    console_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_log_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Optionally, reduce verbosity for specific libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

    logger.debug("Logging has been configured successfully.")
