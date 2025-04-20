import logging
import json

# Configure the logger for the college feedback system
logger = logging.getLogger('college_feedback_system')

def log_info(message, **kwargs):
    """Log info level message"""
    logger.info(message, extra=kwargs)

def log_warning(message, **kwargs):
    """Log warning level message"""
    logger.warning(message, extra=kwargs)

def log_error(message, **kwargs):
    """Log error level message"""
    logger.error(message, extra=kwargs)

def log_exception(message, exc=None, **kwargs):
    """Log exception with traceback"""
    logger.exception(message, exc_info=exc, extra=kwargs) 