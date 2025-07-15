from pathlib import Path
from shutil import copy2
from datetime import datetime

from logs.logger import logger


def backup_file(filepath: Path) -> Path:
    """
    Create a timestamped backup copy of the given file.
    Returns the backup file path.
    """
    logger.info("-" * 60)
    logger.info(f"Starting backup for file: {filepath}")

    if not filepath.exists():
        logger.error(f"File not found, cannot back up: {filepath}")
        raise FileNotFoundError(
            f"{filepath} does not exist and cannot be backed up."
        )

    backup_name = (
        f"{filepath.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        f"{filepath.suffix}"
    )
    backup_dir = filepath.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    backup_path = backup_dir / backup_name

    copy2(filepath, backup_path)
    logger.info(f"Backup created at: {backup_path}")

    return backup_path
