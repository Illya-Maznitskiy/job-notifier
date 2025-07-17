import json
from pathlib import Path

from logs.logger import logger  # Your logger
from storage.backups.backup_file import backup_file


def save_all_vacancies(storage_dir: Path):
    """
    Combines all JSON files in storage_dir into all_vacancies.json.
    Backs up existing all_vacancies.json before overwriting.
    """
    logger.info("-" * 60)
    logger.info(f"Starting save_all_vacancies in {storage_dir}")

    all_vacancies_path = storage_dir / "all_vacancies.json"

    # Gather all JSON files except all_vacancies.json
    json_files = [
        f for f in storage_dir.glob("*.json") if f.name != "all_vacancies.json"
    ]
    logger.info(f"Found {len(json_files)} JSON files to combine")

    combined_data = []

    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    combined_data.extend(data)
                else:
                    logger.warning(
                        f"File {jf} does not contain a list, skipping."
                    )
        except Exception as e:
            logger.error(f"Error reading {jf}: {e}")

    # Save combined data to all_vacancies.json
    try:
        with open(all_vacancies_path, "w", encoding="utf-8") as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
        logger.info(
            f"Saved combined {len(combined_data)} vacancies to {all_vacancies_path}"
        )
    except Exception as e:
        logger.error(f"Failed to save combined vacancies: {e}")

    # Backup existing all_vacancies.json if it exists
    if all_vacancies_path.exists():
        try:
            backup_path = backup_file(all_vacancies_path)
            logger.info(f"Backup created: {backup_path}")
        except Exception as e:
            logger.error(
                f"Failed to create backup for {all_vacancies_path}: {e}"
            )
