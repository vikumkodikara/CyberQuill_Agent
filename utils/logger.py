"""
CyberQuill Logger
==================

Purpose:
    Provides a consistent, structured logging setup for the entire project.
    Every agent calls `get_logger(__name__)` to get a logger that:
    - Prints to the console (for development)
    - Writes to a log file (for the Streamlit Agent Logs page)
    - Includes timestamps, module names, and log levels

Why a custom logger setup?
    Python's built-in `logging` module is powerful but requires setup.
    Without this module, every agent would need to configure logging
    independently, leading to inconsistent formats and missed logs.

Inputs:
    - Logger name (usually __name__ of the calling module)

Outputs:
    - A configured logging.Logger instance

Dependencies:
    - Python standard library (logging, os)
    - config.settings (for LOG_LEVEL)

Testing strategy:
    - Call get_logger("test") and log a message → should appear in console
    - Check that log file is created in logs/ directory
    - Verify log format includes timestamp, level, and module name

Possible improvements:
    - Add JSON-formatted logging for production
    - Add log rotation (e.g., max 5 files, 10MB each)
    - Add remote log shipping (e.g., to a monitoring service)
"""

import logging
import os
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a configured logger.
    
    Args:
        name: The name of the logger. Convention is to pass __name__
              so the logger is named after the module using it.
              Example: get_logger(__name__) in agents/collector.py
              creates a logger named "agents.collector"
    
    Returns:
        A logging.Logger instance with console and file handlers.
    
    How it works:
        1. Creates a logger with the given name
        2. Sets the log level from settings (default: INFO)
        3. Adds a console handler (prints to terminal)
        4. Adds a file handler (writes to logs/cyberquill.log)
        5. Both handlers use the same format
    
    Why check for existing handlers?
        If get_logger() is called multiple times for the same name
        (which happens in Streamlit due to reruns), we don't want
        to add duplicate handlers. That would cause each log message
        to print multiple times.
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers if they already exist (prevents duplicates)
    if logger.handlers:
        return logger

    # Import settings here (not at top) to avoid circular imports
    # because settings.py might import from utils in the future
    from config.settings import settings

    # Set the minimum log level
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Define the log format
    # Example output: 2026-07-21 14:30:00 | INFO | agents.collector | Fetching RSS feeds...
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ---- Console Handler ----
    # Prints log messages to the terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ---- File Handler ----
    # Writes log messages to a file for the Agent Logs page
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)  # Create logs/ directory if it doesn't exist

    file_handler = logging.FileHandler(
        log_dir / "cyberquill.log",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
