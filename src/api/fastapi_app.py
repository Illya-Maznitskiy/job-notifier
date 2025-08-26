import asyncio
import os

from fastapi import FastAPI
import uvicorn

from logs.logger import logger
from src.telegram.telegram_bot import dp, bot
from src.utils.telegram.run_telegram_bot import run_telegram_bot
from src.utils.job_loop import job_process_loop

app = FastAPI()


@app.get("/healthz")
async def health_check():
    logger.info("-" * 60)
    return {"status": "ok"}


@app.on_event("startup")
async def on_startup():
    logger.info("-" * 60)
    logger.info("Starting background job loop")
    # Start job processing loop in background
    asyncio.create_task(job_process_loop())

    logger.info("Starting Telegram bot")
    # Start telegram bot (this will block so run it in background)
    asyncio.create_task(run_telegram_bot(dp, bot))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
