import os

import psutil

from logs.logger import logger


def log_memory() -> None:
    """
    Logs current process memory usage in MB.
    """
    try:
        process = psutil.Process(os.getpid())
        mem_mb = process.memory_info().rss / 1024**2
        logger.info(f"Memory usage: {mem_mb:.2f} MB")
    except Exception as e:
        logger.warning(f"Failed to log memory usage: {e}")
