import logging
import logging.handlers
import os
from datetime import datetime
from config import config

def setup_logger():
    """Setup application logger with file and console handlers."""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('outreach_automation')
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        f'logs/{config.LOG_FILE}',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_operation(operation_type: str, details: dict):
    """Log operation details in a structured format."""
    logger = logging.getLogger('outreach_automation')
    
    log_message = f"{operation_type} - {details}"
    logger.info(log_message)

def log_error(operation_type: str, error: Exception, details: dict = None):
    """Log error details in a structured format."""
    logger = logging.getLogger('outreach_automation')
    
    error_details = {
        'operation': operation_type,
        'error_type': type(error).__name__,
        'error_message': str(error),
        'details': details or {}
    }
    
    logger.error(f"ERROR - {error_details}")

def log_rate_limit(service: str, current_count: int, limit: int):
    """Log rate limiting information."""
    logger = logging.getLogger('outreach_automation')
    logger.warning(f"Rate limit check - {service}: {current_count}/{limit}")

def log_compliance(action: str, recipient: str, compliance_type: str):
    """Log compliance-related actions."""
    logger = logging.getLogger('outreach_automation')
    logger.info(f"COMPLIANCE - {action} for {recipient}: {compliance_type}")

# Initialize logger
logger = setup_logger() 