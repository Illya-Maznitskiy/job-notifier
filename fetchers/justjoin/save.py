import json
from pathlib import Path

from logs.logger import logger


def save_jobs_to_json(jobs, filename="justjoin_jobs.json"):
    """
    Saves job list to JSON file in the storage directory.
    """
    # Get the root directory (the one containing your main script or .git, etc.)
    root_dir = Path(__file__).resolve().parent.parent.parent
    storage_dir = root_dir / "storage"
    storage_dir.mkdir(exist_ok=True)

    filepath = storage_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    logger.info("-" * 60)
    logger.info(f"Saved {len(jobs)} jobs to {filepath}")
