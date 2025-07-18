import json
from pathlib import Path
import os
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from logs.logger import logger

load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage"
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


# Helper to save applied jobs


@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
    if str(message.from_user.id) != os.getenv("ADMIN_ID"):
        await message.answer("You are not allowed to stop the bot.")
        return

    await message.answer("Bot is shutting down...")
    logger.info("Received stop command. Stopping bot.")
    await bot.session.close()
    await dp.stop_polling()


def save_applied():
    with open(APPLIED_FILE, "w", encoding="utf-8") as f:
        json.dump(applied_jobs, f, indent=2, ensure_ascii=False)
    logger.info(
        f"Applied jobs saved. Current size: "
        f"{len(json.dumps(applied_jobs)) / (1024*1024):.2f} MB"
    )


def save_skipped():
    with open(SKIPPED_FILE, "w", encoding="utf-8") as f:
        json.dump(skipped_jobs, f, indent=2, ensure_ascii=False)
    logger.info(
        f"Skipped jobs saved. Current size: "
        f"{len(json.dumps(skipped_jobs)) / (1024*1024):.2f} MB"
    )


# Start command handler
@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    logger.info(f"User {message.from_user.id} started the bot.")
    await message.answer(
        "Hi! I'll send you new Python dev jobs. Use /next to get a vacancy."
    )


@dp.message(Command(commands=["next"]))
async def send_next_vacancy(message: types.Message):
    user_id = str(message.from_user.id)
    logger.info(f"User {user_id} requested next vacancy.")

    # Load vacancies
    if not FILTERED_FILE.exists():
        logger.warning(
            f"Vacancies file not found when user {user_id} requested next job."
        )
        await message.answer("No vacancies found yet.")
        return

    with open(FILTERED_FILE, "r", encoding="utf-8") as f:
        vacancies = json.load(f)

    logger.debug(f"Total vacancies loaded: {len(vacancies)}")

    user_applied = applied_jobs.get(user_id, [])
    user_skipped = skipped_jobs.get(user_id, [])
    logger.info(f"User {user_id} has applied to {len(user_applied)} jobs.")
    logger.debug(f"Applied jobs: {user_applied}")
    logger.debug(f"Skipped jobs: {user_skipped}")

    for job in vacancies:
        logger.debug(f"Checking job '{job['title']}' against user history.")
        if (
            job["title"] not in user_applied
            and job["title"] not in user_skipped
        ):
            logger.debug(
                f"Job '{job['title']}' passed filter "
                f"for user {user_id}. Preparing to send."
            )
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Applied ✅",
                            callback_data=f"applied|{job['title']}",
                        ),
                        InlineKeyboardButton(
                            text="Skip ⏭️",
                            callback_data=f"skip|" f"{job['title']}",
                        ),
                    ]
                ]
            )
            score = job.get(
                "score", "No score"
            )  # or 0 if numeric and you want default 0

            url = job.get("url", "")
            url_text = f"[Link]({url})" if url else "No URL provided"

            msg = (
                f"**{job.get('title', 'No Title')}**\n"
                f"*Company:* {job.get('company', 'Unknown')}\n"
                f"*Score:* {score}\n"
                f"*URL:* {url_text}\n\n"
                f"{job.get('description', '')[:500]}..."
            )

            logger.info(f"Sending job '{job['title']}' to user {user_id}.")
            await message.answer(
                msg, reply_markup=keyboard, parse_mode="Markdown"
            )
            return
        else:
            logger.debug(
                f"Job '{job['title']}' filtered out for user {user_id}."
            )

    logger.info(f"No new vacancies to show for user {user_id}.")
    await message.answer("No new vacancies to show. Check back later!")


# Callback handler for buttons


@dp.callback_query(
    lambda c: c.data and c.data.startswith(("applied|", "skip|"))
)
async def process_callback(callback_query: types.CallbackQuery):
    action, title = callback_query.data.split("|", 1)
    user_id = str(callback_query.from_user.id)

    logger.info(f"User {user_id} clicked '{action}' for job '{title}'.")

    if action == "applied":
        applied_jobs.setdefault(user_id, []).append(title)
        save_applied()
        logger.info(f"Marked job '{title}' as applied for user {user_id}.")
        await bot.answer_callback_query(
            callback_query.id, text="Marked as applied!"
        )
        await bot.send_message(user_id, f"Great! Marked '{title}' as applied.")
    elif action == "skip":
        skipped_jobs.setdefault(user_id, []).append(title)
        save_skipped()
        logger.info(f"Marked job '{title}' as skipped for user {user_id}.")
        await bot.answer_callback_query(callback_query.id, text="Skipped.")


async def main():
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)
    logger.info("Bot polling stopped.")


if __name__ == "__main__":
    asyncio.run(main())
