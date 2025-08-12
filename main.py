import asyncio
import os

from fastapi import FastAPI

from logs.logger import logger
from notifier.email_sender import send_job_listings_email
from notifier.telegram.telegram_bot import dp, bot
from utils.fetch_orchestrator import run_all_fetchers
from utils.jobs_saving_processes import save_backup_and_filter_jobs
from utils.run_telegram_bot import run_telegram_bot

app = FastAPI()


@app.get("/healthz")
async def health_check():
    return {"status": "ok"}


async def job_process_loop():
    """
    Periodically runs job fetching, saving, emailing.
    Runs every 12 hour.
    """
    while True:
        logger.info("-" * 60)
        logger.info("Job processing started")

        await run_all_fetchers()
        save_backup_and_filter_jobs()
        send_job_listings_email()

        await asyncio.sleep(12 * 3600)  # wait 12 hours before next fetch


@app.on_event("startup")
async def on_startup():
    # Start job processing loop in background
    asyncio.create_task(job_process_loop())
    # Start telegram bot (this will block so run it in background)
    asyncio.create_task(run_telegram_bot(dp, bot))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
