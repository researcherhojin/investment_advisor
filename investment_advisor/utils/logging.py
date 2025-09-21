"""
Logging Configuration

Centralized logging setup for the application.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import re

import streamlit as st


class RepetitiveMessageFilter(logging.Filter):
    """Filter to reduce repetitive log messages."""

    def __init__(self):
        super().__init__()
        self.last_messages = {}
        self.message_counts = {}
        self.max_repeat = 3  # Show message at most 3 times

        # Patterns to skip entirely
        self.skip_patterns = [
            r"Failed download:",
            r"possibly delisted",
            r"Failed to get ticker",
            r"Failed to batch ingest runs",
            r"No data found for .* with date range",
            r"Logging configured with level",
            r"\$.*: possibly delisted",
            r"JSONDecodeError\('Expecting value:",
            r"YFTzMissingError",
            r"429 Client Error: Too Many Requests",
            r"\d+ Failed download:",
            r"Failed to get ticker '.*' reason:",
            r"Error writing cache: keys must be",
        ]

        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern) for pattern in self.skip_patterns]

    def filter(self, record):
        """Filter repetitive messages."""
        msg = record.getMessage()

        # Skip certain repetitive messages entirely
        for pattern in self.compiled_patterns:
            if pattern.search(msg):
                return False

        # For other messages, limit repetition
        msg_hash = hash(msg[:100])  # Use first 100 chars for hash

        if msg_hash in self.message_counts:
            self.message_counts[msg_hash] += 1
            if self.message_counts[msg_hash] > self.max_repeat:
                return False
        else:
            self.message_counts[msg_hash] = 1

        return True


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        max_file_size: Maximum log file size in bytes
        backup_count: Number of backup files to keep

    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger("investment_advisor")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler with repetitive message filter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RepetitiveMessageFilter())
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        try:
            # Create log directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # Rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, log_level.upper()))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            logger.info(f"File logging enabled: {log_file}")

        except Exception as e:
            logger.error(f"Failed to set up file logging: {e}")

    # Set up third-party library loggers
    _configure_third_party_loggers(log_level)

    # Only log this once at startup
    if not hasattr(logger, '_already_configured'):
        logger.info(f"Logging configured with level: {log_level}")
        logger._already_configured = True

    return logger


def _configure_third_party_loggers(log_level: str) -> None:
    """Configure logging for third-party libraries."""

    # Reduce verbosity of some third-party loggers
    third_party_loggers = [
        "httpx",
        "httpcore",
        "requests",
        "urllib3",
        "yfinance",
        "matplotlib",
        "plotly",
        "langsmith",
        "langchain",
    ]

    # Set third-party loggers to WARNING level to reduce noise
    third_party_level = logging.WARNING if log_level.upper() in ["DEBUG", "INFO"] else getattr(logging, log_level.upper())

    for logger_name in third_party_loggers:
        logging.getLogger(logger_name).setLevel(third_party_level)

    # Special handling for some loggers
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
    logging.getLogger("yfinance.utils").setLevel(logging.ERROR)
    logging.getLogger("langsmith.client").setLevel(logging.ERROR)

    # Suppress yfinance download messages
    logging.getLogger("yfinance").setLevel(logging.ERROR)


class StreamlitLogHandler(logging.Handler):
    """Custom logging handler for Streamlit applications."""

    def __init__(self):
        super().__init__()
        self.logs = []

    def emit(self, record):
        """Emit log record to Streamlit."""
        try:
            msg = self.format(record)
            self.logs.append({
                'level': record.levelname,
                'message': msg,
                'timestamp': record.created
            })

            # Keep only last 100 logs to prevent memory issues
            if len(self.logs) > 100:
                self.logs = self.logs[-100:]

            # Display in Streamlit based on level
            if record.levelno >= logging.ERROR:
                st.error(record.getMessage())
            elif record.levelno >= logging.WARNING:
                st.warning(record.getMessage())
            elif record.levelno >= logging.INFO:
                st.info(record.getMessage())

        except Exception:
            self.handleError(record)

    def get_logs(self, level: Optional[str] = None, limit: int = 50):
        """Get recent logs, optionally filtered by level."""
        logs = self.logs[-limit:]

        if level:
            logs = [log for log in logs if log['level'] == level.upper()]

        return logs


def get_streamlit_log_handler() -> StreamlitLogHandler:
    """Get or create Streamlit log handler."""
    # Check if handler already exists
    logger = logging.getLogger("investment_advisor")

    for handler in logger.handlers:
        if isinstance(handler, StreamlitLogHandler):
            return handler

    # Create new handler
    st_handler = StreamlitLogHandler()
    st_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    st_handler.setFormatter(formatter)

    logger.addHandler(st_handler)
    return st_handler


def log_function_call(func):
    """Decorator to log function calls (for debugging)."""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger("investment_advisor")
        logger.debug(f"Calling {func.__name__} with args={args[:2]}... kwargs={list(kwargs.keys())}")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}")
            raise

    return wrapper


def log_performance(func):
    """Decorator to log function performance."""
    import time

    def wrapper(*args, **kwargs):
        logger = logging.getLogger("investment_advisor")
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} completed in {duration:.2f} seconds")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.2f} seconds: {e}")
            raise

    return wrapper
