#decorators.py

import logging
from functools import wraps

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