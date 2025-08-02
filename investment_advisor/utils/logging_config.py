"""
Logging Configuration

Centralized logging configuration to suppress unwanted messages.
"""

import logging
import sys
from typing import Optional


def configure_logging(log_level: str = "INFO", suppress_external: bool = True):
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        suppress_external: Whether to suppress external library logs
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with custom formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    if suppress_external:
        # Suppress noisy external libraries
        suppress_libraries = [
            'yfinance',
            'urllib3',
            'requests',
            'httpx',
            'asyncio',
            'concurrent.futures',
            'matplotlib',
            'PIL',
            'fsspec',
            'numexpr',
            'peewee',  # yfinance dependency
        ]
        
        for lib in suppress_libraries:
            logging.getLogger(lib).setLevel(logging.WARNING)
        
        # Specifically suppress yfinance download messages
        logging.getLogger('yfinance.utils').setLevel(logging.ERROR)
        logging.getLogger('yfinance.download').setLevel(logging.ERROR)
    
    # Suppress Streamlit warnings about missing ScriptRunContext
    logging.getLogger('streamlit.runtime.scriptrunner').setLevel(logging.ERROR)
    
    # Add custom filter to suppress ScriptRunContext warnings
    class StreamlitThreadFilter(logging.Filter):
        def filter(self, record):
            # Filter out ScriptRunContext warnings
            message = record.getMessage()
            if "missing ScriptRunContext" in message:
                return False
            if "ThreadPoolExecutor" in message and "missing ScriptRunContext" in message:
                return False
            return True
    
    # Apply filter to all loggers
    for handler in root_logger.handlers:
        handler.addFilter(StreamlitThreadFilter())
    
    return root_logger


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with optional custom level.
    
    Args:
        name: Logger name (usually __name__)
        level: Optional custom log level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if level:
        logger.setLevel(getattr(logging, level.upper()))
    
    return logger


# Suppress yfinance print statements
class SuppressYfinancePrints:
    """Context manager to suppress yfinance print statements."""
    
    def __enter__(self):
        import io
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr