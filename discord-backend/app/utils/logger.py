# app/utils/logger.py
import logging
import sys
from typing import Optional
from datetime import datetime

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration"""
    log_level = getattr(logging, level.upper())
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=handlers
    )

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get logger instance"""
    if name:
        return logging.getLogger(name)
    return logging.getLogger(__name__)

class LogContext:
    """Context manager for logging with extra context"""
    def __init__(self, logger: logging.Logger, message: str, **kwargs):
        self.logger = logger
        self.message = message
        self.kwargs = kwargs
    
    async def __aenter__(self):
        self.logger.info(f"{self.message} - Started", extra=self.kwargs)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error(f"{self.message} - Failed: {exc_val}", extra=self.kwargs)
        else:
            self.logger.info(f"{self.message} - Completed", extra=self.kwargs)
    
    def __enter__(self):
        self.logger.info(f"{self.message} - Started", extra=self.kwargs)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error(f"{self.message} - Failed: {exc_val}", extra=self.kwargs)
        else:
            self.logger.info(f"{self.message} - Completed", extra=self.kwargs)