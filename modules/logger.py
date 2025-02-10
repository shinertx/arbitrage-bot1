# modules/logger.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name, level=logging.INFO, log_file=None):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Clear any existing handlers.
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console handler.
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler, if log_file is provided.
    if log_file:
        fh = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
    return logger
