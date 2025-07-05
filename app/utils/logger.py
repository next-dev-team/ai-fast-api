import logging
import sys
from typing import Optional
from ..config import settings


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Setup and configure logger."""
    logger = logging.getLogger(name or __name__)
    
    # Avoid adding multiple handlers
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = logging.DEBUG if settings.debug else logging.INFO
    logger.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


# Global logger instance
logger = setup_logger("ai-fastapi")