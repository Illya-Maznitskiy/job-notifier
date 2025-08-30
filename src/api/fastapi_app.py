import asyncio
import os

from fastapi import FastAPI, Request
import uvicorn

from logs.logger import logger
from src.telegram.telegram_bot import start_bot
from src.utils.job_loop import job_process_loop

app = FastAPI()


@app.api_route("/healthz", methods=["GET", "HEAD", "POST", "OPTIONS"])
async def health_check(request: Request):
    logger.info("-" * 60)
    logger.info(f"Health check received: {request.method}")
    return {"status": "ok"}


@app.on_event("startup")
async def on_startup():
    logger.info("-" * 60)
    logger.info("Starting background job loop")
    # Start job processing loop in background
    asyncio.create_task(job_process_loop())

    logger.info("Starting Telegram bot")
    # Start telegram bot (this will block so run it in background)
    asyncio.create_task(start_bot())


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
