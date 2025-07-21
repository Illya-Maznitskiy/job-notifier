import json
import os
from pathlib import Path

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from logs.logger import logger


load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage"
FILTERED_FILE = STORAGE_DIR / "filtered_vacancies.json"
APPLIED_FILE = STORAGE_DIR / "applied_jobs.json"
SKIPPED_FILE = STORAGE_DIR / "skipped_jobs.json"


# Load skipped jobs
if SKIPPED_FILE.exists() and SKIPPED_FILE.stat().st_size > 0:
    try:
        with open(SKIPPED_FILE, "r", encoding="utf-8") as f:
            skipped_jobs = json.load(f)
    except json.JSONDecodeError:
        skipped_jobs = {}
        logger.warning(
            f"{SKIPPED_FILE} contains invalid JSON. Initialized empty."
        )
else:
    skipped_jobs = {}
    logger.info(f"{SKIPPED_FILE} is missing or empty. Initialized empty.")

# Load applied jobs
if APPLIED_FILE.exists() and APPLIED_FILE.stat().st_size > 0:
    try:
        with open(APPLIED_FILE, "r", encoding="utf-8") as f:
            applied_jobs = json.load(f)
    except json.JSONDecodeError:
        applied_jobs = {}
        logger.warning(
            f"{APPLIED_FILE} contains invalid JSON. Initialized empty."
        )
else:
    applied_jobs = {}
    logger.info(f"{APPLIED_FILE} is missing or empty. Initialized empty.")
