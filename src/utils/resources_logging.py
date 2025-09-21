import os

import psutil

from logs.logger import logger


def log_resources() -> None:
    """
    Logs current process memory and CPU usage.
    """
    try:
        process = psutil.Process(os.getpid())
        mem_mb = process.memory_info().rss / 1024**2
        cpu_percent = psutil.cpu_percent(
            interval=1.0
        )
        logger.info(
            f"Resources usage: {mem_mb:.2f} MB | CPU: {cpu_percent:.2f}%"
        )
    except Exception as e:
        logger.warning(f"Failed to log resources: {e}")
