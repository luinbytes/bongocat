"""Logging configuration for Bongo Cat application."""

import os
import sys
import logging
from typing import Optional


def setup_logging(name: str = "BongoCat", log_dir: Optional[str] = None) -> logging.Logger:
    """Set up basic logging configuration.

    Args:
        name: Name of the logger
        log_dir: Directory to store log files. If None, uses APPDATA/BongoCat

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logging()
        >>> logger.info("Application started")
    """
    if log_dir is None:
        appdata = os.getenv("APPDATA")
        if appdata is None:
            appdata = os.path.expanduser("~/.config")
        log_dir = os.path.join(appdata, "BongoCat")

    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "bongo.log")

    # Set up logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='w'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(name)
