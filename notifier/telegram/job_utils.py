import json
import hashlib
from logs.logger import logger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def save_applied(applied_jobs, path):
    """Save applied jobs data to JSON file."""
    logger.info("-" * 60)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(applied_jobs, f, indent=2, ensure_ascii=False)

    total_applied = sum(len(jobs) for jobs in applied_jobs.values())
    logger.info(
        f"Applied jobs saved. Total applied jobs count: {total_applied}"
    )


def save_skipped(skipped_jobs, path):
    """Save skipped jobs data to JSON file."""
    logger.info("-" * 60)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(skipped_jobs, f, indent=2, ensure_ascii=False)

    total_skipped = sum(len(jobs) for jobs in skipped_jobs.values())
    logger.info(
        f"Skipped jobs saved. Total skipped jobs count: {total_skipped}"
    )


def find_job_by_hash(job_hash, filtered_file_path):
    """Find job in file by its hash."""
    logger.info("-" * 60)
    logger.info(f"Looking for job with hash: {job_hash}")

    with open(filtered_file_path, "r", encoding="utf-8") as f:
        all_jobs = json.load(f)
        for job in all_jobs:
            h = hashlib.md5(job["title"].encode("utf-8")).hexdigest()[:16]
            if h == job_hash:
                logger.info(f"Job found: {job['title']}")
                return job
    logger.warning(f"No job found for hash: {job_hash}")

    return None


def get_keyboard(title):
    """Return inline keyboard for given job title."""
    logger.info("-" * 60)

    def get_callback_data(action):
        job_hash = hashlib.md5(title.encode("utf-8")).hexdigest()[:16]
        return f"{action}|{job_hash}"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Applied ✅",
                    callback_data=get_callback_data("applied"),
                ),
                InlineKeyboardButton(
                    text="Skip ⏭️",
                    callback_data=get_callback_data("skip"),
                ),
            ]
        ]
    )
