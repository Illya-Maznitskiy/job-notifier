import json
import os
from collections import defaultdict
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
MEME_GIFS = [
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExa293a3lpNjA0cTJkemE0ZGlienhzZTdjbXltbTh2YXk1aG53a2ptcyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/gidMR0Kv3ljSivshKJ/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExd24xYWd2dmJvd2FtbXpxNnJ2dTBhbXE5ajFmamp3NmwxOXl5NTk1dCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/bNpLfNOskgvGIfKIZN/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcHliYnd2cmM2NHM5MHdobzNhMWd0cTluZmgzZjJxb21yMDBxanhjMCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/lEADCfIrDg5fMyb3ca/giphy.gif/media/l2JhB29QUPw6xD5eE/giphy.gif",
    "https://tenor.com/view/wake-up-cat-cat-meme-cat-motivation-meme-cat-motivation-gif-13680646881934680723",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXdoeDZkdXV6d2MweWIzbWZjYmpjaWdkeTFsYmxndDhiaDlqeW96ayZlcD12MV9naWZzX3NlYXJjaCZjdD1n/zaciDLCM6xGyi51kwB/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3eHNtMTB0YXZxYmthdDkydmQ3ZGg0eTNzYTNpdjJvcWJmengybzY5NyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/2RGhmKXcl0ViM/giphy.gif",
    "https://tenor.com/view/stay-hard-gif-26958197",
    "https://tenor.com/view/i-am-back-mother-fucker-david-goggins-gif-25850195",
]


user_request_count = defaultdict(int)


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
