import asyncio
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
import uvicorn

from logs.logger import logger
from src.telegram.telegram_bot import start_bot

from src.utils.fetching.job_loop import job_process_loop

app = FastAPI()
bot_started = False


@app.api_route("/healthz", methods=["GET", "HEAD", "POST", "OPTIONS"])
async def health_check(request: Request) -> dict:
    """Return service health status."""
    logger.info("-" * 60)
    logger.info(f"Health check received: {request.method}")
    return {"status": "ok"}


@asynccontextmanager
async def lifespan(_fastapi_app: FastAPI) -> AsyncIterator[None]:
    """Start background jobs and Telegram bot."""
    global bot_started

    logger.info("-" * 60)
    logger.info("Starting background job loop")

    asyncio.create_task(job_process_loop())

    if not bot_started:
        bot_started = True
        logger.info("Starting Telegram bot")
        asyncio.create_task(start_bot())

    yield

    logger.info("Stopping background jobs and Telegram bot")


app.router.lifespan_context = lifespan


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
