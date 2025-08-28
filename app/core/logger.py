# app/core/logger.py
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

def setup_logger(name: str, level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup and configure logger with both console and file handlers
    
    Args:
        name: Logger name (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    
    Returns:
        Configured logger instance
    """
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatter
    console_formatter = ColoredFormatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Get or create logger instance with default configuration
    
    Args:
        name: Logger name (usually __name__)
        level: Log level
        
    Returns:
        Logger instance
    """
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Generate log file name with current date
    current_date = datetime.now().strftime("%Y%m%d")
    log_file = logs_dir / f"ipdr_analysis_{current_date}.log"
    
    return setup_logger(name, level, str(log_file))

# Application-wide logger instance
app_logger = get_logger("ipdr_app")

def log_function_call(func_name: str, args: dict = None, result: str = None):
    """Helper function to log function calls for debugging"""
    app_logger.debug(f"Function: {func_name}")
    if args:
        app_logger.debug(f"Arguments: {args}")
    if result:
        app_logger.debug(f"Result: {result}")

def log_error(error: Exception, context: str = ""):
    """Helper function to log errors with context"""
    error_msg = f"Error in {context}: {type(error).__name__}: {str(error)}"
    app_logger.error(error_msg)

def log_performance(func_name: str, execution_time: float):
    """Helper function to log performance metrics"""
    app_logger.info(f"Performance: {func_name} executed in {execution_time:.3f} seconds")
