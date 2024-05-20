import logging

import config


def get_logger(name: str) -> logging.Logger:
    """
    Create and configure a logger with the given name.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The configured logger instance.
    """
    # Configure logging
    logging.basicConfig(
        filename=config.LOG_FILE, filemode="a", format=config.LOG_FORMAT
    )
    logger = logging.getLogger(name)
    logger.setLevel(level=logging.INFO)

    # Create a stream handler to output to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(config.LOG_FORMAT))

    # Add the stream handler to the logger
    logger.addHandler(console_handler)
    return logger
