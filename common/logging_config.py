"""
Usage:
    from common.logging_config import setup_logging
    logger = setup_logging(__name__)
    logger.info("Service started")

    Input:
        name: Logger name (typically __name__ from calling module)
        level: Logging level (default: INFO)
        format_string: Optional custom format string
    returns:
        Configured logger instance

    Example:
        >>> logger = setup_logging(__name__)
        >>> logger.info("✅ Service initialized")
"""

import logging
from typing import Optional


def setup_logging(name: str, level: int = logging.INFO, format_string: Optional[str] = None) -> logging.Logger:
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Only configure root logger once
    if not logging.getLogger().handlers:
        logging.basicConfig(level=level, format=format_string)

    # Return logger for the specific module
    logger = logging.getLogger(name)
    return logger
