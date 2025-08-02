"""
Streamlit Context Manager

Handles Streamlit context for concurrent operations.
"""

import streamlit as st
from contextlib import contextmanager
import threading
from typing import Optional, Callable, Any
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def get_streamlit_script_run_ctx():
    """Get the current Streamlit script run context."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx()
    except ImportError:
        # Fallback for older Streamlit versions
        try:
            from streamlit.script_run_context import get_script_run_ctx
            return get_script_run_ctx()
        except ImportError:
            return None


def streamlit_thread_wrapper(func: Callable) -> Callable:
    """Wrapper to preserve Streamlit context in threads."""
    @wraps(func)
    def wrapped(*args, **kwargs):
        # Get the current context
        ctx = get_streamlit_script_run_ctx()
        
        if ctx is None:
            # No context to preserve, run normally
            return func(*args, **kwargs)
        
        # Try to add context to the current thread
        try:
            from streamlit.runtime.scriptrunner import add_script_run_ctx
            
            # Create a wrapper function that will run in the thread
            def thread_func():
                return func(*args, **kwargs)
            
            # Add context and run
            contextualized_func = add_script_run_ctx(thread_func, ctx)
            return contextualized_func()
            
        except ImportError:
            try:
                # Fallback for older versions
                from streamlit.script_run_context import add_script_run_ctx
                
                def thread_func():
                    return func(*args, **kwargs)
                
                contextualized_func = add_script_run_ctx(thread_func, ctx)
                return contextualized_func()
                
            except ImportError:
                # If we can't add context, just run the function
                logger.warning("Cannot add Streamlit context - running without context")
                return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error adding Streamlit context: {e}")
            return func(*args, **kwargs)
    
    return wrapped


def add_streamlit_script_run_ctx(func: Callable) -> Callable:
    """Simple wrapper that returns a contextualized version of the function."""
    return streamlit_thread_wrapper(func)


@contextmanager
def streamlit_thread_context():
    """Context manager for running code in threads with Streamlit context."""
    ctx = get_streamlit_script_run_ctx()
    if ctx is None:
        yield
        return
    
    # Store context in thread local storage
    original_ctx = getattr(threading.current_thread(), '_streamlit_script_run_ctx', None)
    threading.current_thread()._streamlit_script_run_ctx = ctx
    
    try:
        yield
    finally:
        # Restore original context
        if original_ctx is None:
            delattr(threading.current_thread(), '_streamlit_script_run_ctx')
        else:
            threading.current_thread()._streamlit_script_run_ctx = original_ctx


def safe_thread_callback(callback: Callable):
    """Wrap a callback to safely run in a thread with Streamlit context."""
    def wrapped(*args, **kwargs):
        with streamlit_thread_context():
            try:
                return callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in thread callback: {e}")
                raise
    
    return wrapped