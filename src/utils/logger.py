"""
Logging utility for the Who Wants to Be a Millionaire game.
Provides consistent logging format and functionality across all components.
"""

import os
import sys
from pathlib import Path
from loguru import logger
import threading

def setup_logger():
    """
    Configure the logger with console and file handlers.
    Creates necessary directories and sets up log rotation.
    """
    try:
        # Create logs directory in the project root
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # Remove default handler
        logger.remove()
        
        # Add console handler with color for INFO level and above
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO",
            backtrace=True,
            diagnose=True
        )
        
        # Add file handler for all DEBUG level and above
        log_file = log_dir / "debug_{time}.log"
        logger.add(
            str(log_file),
            rotation="500 MB",
            retention="10 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            backtrace=True,
            diagnose=True,
            enqueue=True  # Thread-safe logging
        )
        
        # Add error file handler for ERROR level and above
        error_file = log_dir / "error_{time}.log"
        logger.add(
            str(error_file),
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            backtrace=True,
            diagnose=True,
            enqueue=True  # Thread-safe logging
        )
        
    except Exception as e:
        print(f"Failed to setup logger: {e}", file=sys.stderr)
        sys.exit(1)

def get_logger(name):
    """
    Get a logger instance with the specified name.
    
    Args:
        name (str): Name of the logger, typically __name__ of the module
        
    Returns:
        logger: Configured logger instance with context
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
        >>> logger.debug("Processing data...")
        >>> logger.error("An error occurred", exc_info=True)
    """
    try:
        return logger.bind(
            name=name,
            context={
                "module": name,
                "pid": os.getpid(),
                "thread": threading.current_thread().name
            }
        )
    except Exception as e:
        print(f"Failed to create logger for {name}: {e}", file=sys.stderr)
        return logger.bind(name=name)  # Fallback to simple binding

# Setup logger when module is imported
setup_logger() 