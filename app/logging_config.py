import logging
import logging.handlers
import sys
from pathlib import Path


def add_console_handler(logger: logging.Logger, formatter: logging.Formatter):
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def add_file_handler(logger: logging.Logger, formatter: logging.Formatter, log_file: str):
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10_000_000,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def setup_logging(*, log_level: int = logging.INFO, log_file: str = "logs/app.log", log_to_file: bool = True, log_to_console: bool = False):
    """
    Configure logging for the application
    """
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if log_to_console:
        add_console_handler(root_logger, formatter)

    if log_to_file:
        add_file_handler(root_logger, formatter, log_file)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return root_logger
