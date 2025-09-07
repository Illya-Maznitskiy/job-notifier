import asyncio
import os

from fastapi import FastAPI, Request
import uvicorn

from logs.logger import logger
from src.telegram.telegram_bot import start_bot

app = FastAPI()
bot_started = False


@app.api_route("/healthz", methods=["GET", "HEAD", "POST", "OPTIONS"])
async def health_check(request: Request):
    logger.info("-" * 60)
    logger.info(f"Health check received: {request.method}")
    return {"status": "ok"}


@app.on_event("startup")
async def on_startup():
    global bot_started
    logger.info("-" * 60)
    logger.info("Starting background job loop")
    # Start job processing loop in background
    # asyncio.create_task(job_process_loop())

    if not bot_started:
        # Start telegram bot (this will block so run it in background)
        bot_started = True
        logger.info("Starting Telegram bot")
        asyncio.create_task(start_bot())
        logger.info("Startup complete. Telegram bot running in background.")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
