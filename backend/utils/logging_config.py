"""
Logging configuration for tax-loss harvesting system.
"""

import logging
import logging.handlers
import os
from datetime import datetime

# Create logs directory
os.makedirs("./logs", exist_ok=True)

# Define log file paths
log_dir = "./logs"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(log_dir, f"tax_harvesting_{timestamp}.log")


def setup_logging():
    """Configure centralized logging system."""
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter with context
    formatter = logging.Formatter(
        '%(asctime)s - [%(name)s] - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger


class ContextFilter(logging.Filter):
    """Add context information to logs."""
    
    def __init__(self, context_id=None, user_id=None):
        super().__init__()
        self.context_id = context_id
        self.user_id = user_id
    
    def filter(self, record):
        """Add context to record."""
        record.context_id = self.context_id or "N/A"
        record.user_id = self.user_id or "N/A"
        return True


def get_context_logger(name, context_id=None, user_id=None):
    """Get logger with context information."""
    logger = logging.getLogger(name)
    context_filter = ContextFilter(context_id, user_id)
    logger.addFilter(context_filter)
    return logger


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
