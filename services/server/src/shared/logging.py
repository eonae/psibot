import logging
import sys
import time


def setup_logging(level):
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [handler]


def redact_text(text: str) -> str:
    """Маскирует чувствительные данные, оставляя видимыми только последние 4 символа"""
    if len(text) <= 4:
        return "*" * len(text)

    return "*" * (len(text) - 4) + text[-4:]


def log_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(
            "⏱️ Execution time of %s: %.4f seconds", func.__name__, execution_time
        )
        return result

    return wrapper
