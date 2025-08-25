import os

import uvicorn
import asyncio

from src.utils.fastapi_app import app
from src.utils.job_loop import job_process_loop


def main():
    """Start FastAPI server and background job loop"""
    # Start background job loop
    asyncio.create_task(job_process_loop())

    # Run FastAPI server
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
