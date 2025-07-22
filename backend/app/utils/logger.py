import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logger(name: str = "co_scientist", level: str = None) -> logging.Logger:
    """Set up application logger with file and console output"""
    
    # Get log level from environment or default to INFO
    log_level = level or os.getenv("LOG_LEVEL", "INFO").upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Avoid adding multiple handlers
    if logger.handlers:
        return logger
    
    # Create log directory
    log_dir = Path(os.getenv("LOG_DIR", "./logs"))
    log_dir.mkdir(exist_ok=True)
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

# Create default logger instance
default_logger = setup_logger()

def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance"""
    if name:
        return setup_logger(name)
    return default_logger 