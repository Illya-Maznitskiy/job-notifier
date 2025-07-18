import json
import os
from pathlib import Path

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher


load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage"
FILTERED_FILE = STORAGE_DIR / "filtered_vacancies.json"
APPLIED_FILE = STORAGE_DIR / "applied_jobs.json"
SKIPPED_FILE = STORAGE_DIR / "skipped_jobs.json"

if SKIPPED_FILE.exists():
    with open(SKIPPED_FILE, "r", encoding="utf-8") as f:
        skipped_jobs = json.load(f)
else:
    skipped_jobs = {}


# Load applied jobs to avoid resending
if APPLIED_FILE.exists():
    with open(APPLIED_FILE, "r", encoding="utf-8") as f:
        applied_jobs = json.load(f)
else:
    applied_jobs = {}
# Load once into memory
applied_jobs = json.load(open(APPLIED_FILE)) if APPLIED_FILE.exists() else {}
skipped_jobs = json.load(open(SKIPPED_FILE)) if SKIPPED_FILE.exists() else {}
