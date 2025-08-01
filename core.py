import logging
import functools
import uuid
from flask import jsonify

# 1. Centralized Logging Setup
def setup_logging():
    """
    Sets up a centralized logging configuration for the entire application.
    """
    # Create a logger instance
    logger = logging.getLogger('api_hub')
    logger.setLevel(logging.INFO)

    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Create file handler and set level to info
    fh = logging.FileHandler('api_hub.log')
    fh.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add the formatter to the handlers
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger

# Initialize the logger
logger = setup_logging()

# 2. Error Handling Decorator with Unique ID
def handle_api_errors(func):
    """
    A decorator to handle exceptions from API calls.
    It logs the error with a unique ID and returns a standardized error message.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Generate a unique ID for the error
            error_id = str(uuid.uuid4())
            logger.error(f"Error ID: {error_id} - An error occurred in function '{func.__name__}': {e}", exc_info=True)
            # Return a user-friendly message including the unique error ID
            return jsonify({
                "status": "error",
                "message": f"An unexpected error occurred. Please reference this error ID: {error_id}"
            }), 500
    return wrapper