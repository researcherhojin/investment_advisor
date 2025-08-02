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
    
    # Remove existing handlers to prevent duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Prevent propagation to avoid duplicate messages
    root_logger.propagate = False
    
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
    logging.getLogger('streamlit.runtime.scriptrunner_utils.script_run_context').setLevel(logging.ERROR)
    logging.getLogger('streamlit.runtime.state.session_state_proxy').setLevel(logging.ERROR)
    
    # Add custom filter to suppress ScriptRunContext warnings
    class StreamlitThreadFilter(logging.Filter):
        def filter(self, record):
            # Filter out ScriptRunContext and ThreadPoolExecutor warnings
            message = record.getMessage()
            if any(phrase in message for phrase in [
                "missing ScriptRunContext",
                "ThreadPoolExecutor",
                "Session state does not function",
                "script without `streamlit run`"
            ]):
                return False
            return True
    
    # Apply filter to all loggers
    for handler in root_logger.handlers:
        handler.addFilter(StreamlitThreadFilter())
    
    # Configure specific loggers to prevent duplicate messages
    for logger_name in [
        'investment_advisor.analysis.decision_system',
        'investment_advisor.data.stable_fetcher',
        'investment_advisor.data.simple_fetcher',
        'investment_advisor.agents.company_analyst',
        'investment_advisor.agents.technical_analyst'
    ]:
        logger = logging.getLogger(logger_name)
        logger.propagate = False
        if not logger.handlers:
            logger.addHandler(console_handler)
    
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