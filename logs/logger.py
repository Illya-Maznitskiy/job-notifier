import logging
import sys
import os
from datetime import datetime
from pathlib import Path


# Create logs directory if it doesn't exist
# Get root directory (two levels up if this file is in a subfolder)
root_dir = Path(__file__).resolve().parent.parent
log_dir = root_dir / "logs"
log_dir.mkdir(exist_ok=True)
log_level = logging.INFO

# Log filename with timestamp
log_filename = os.path.join(
    log_dir, f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)

# Create logs instance
logger = logging.getLogger("job_notifier_logger")
logger.setLevel(log_level)

# Console handler for terminal output
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(log_level)
console_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_format)

# File handler for logging info and higher-level messages to file
file_handler = logging.FileHandler(log_filename, encoding="utf-8")
file_handler.setLevel(log_level)
file_format = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
file_handler.setFormatter(file_format)

# Add handlers to logs
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.propagate = False
