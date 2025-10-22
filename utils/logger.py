
# utils/logger.py
import logging
import sys

def setup_logger(name: str, log_file: str = 'ssv_monetization.log', level=logging.INFO):
    """Функция для настройки логгера."""
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger
