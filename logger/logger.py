import logging
import os
from logging import Logger
from logging.handlers import RotatingFileHandler


def get_logger(name: str = "ai_trip_planner", log_file: str = "logs/app.log") -> Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        console_handler = logging.StreamHandler()
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    return logger
