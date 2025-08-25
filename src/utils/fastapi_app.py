import asyncio
import os

from fastapi import FastAPI
import uvicorn

from logs.logger import logger
from src.utils.email_sender import send_job_listings_email
from src.telegram import dp, bot
from src.utils import run_all_fetchers
from src.utils import run_telegram_bot


app = FastAPI()


@app.get("/healthz")
async def health_check():
    return {"status": "ok"}


@app.on_event("startup")
async def on_startup():
    # Start job processing loop in background
    asyncio.create_task(job_process_loop())
    # Start telegram bot (this will block so run it in background)
    asyncio.create_task(run_telegram_bot(dp, bot))


if __name__ == "__main__":

    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
