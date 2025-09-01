import os
import uvicorn
import asyncio
from src.api.fastapi_app import app


async def main():
    """Start FastAPI server and background job loop"""
    # Run FastAPI server
    port = int(os.getenv("PORT", 8000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())


# TODO:
#   Delete previous jobs while new fetching
#   Add delete all keywords command
#   Clean telegram package, add simple docs, type annotation, logging to each function
#   Clean db package, add simple docs, type annotation, logging to each function
#   Clean api package, add simple docs, type annotation, logging to each function
#   Clean utils package, add simple docs, type annotation, logging to each function
#   Use type hints and short docstrings (max 12 words).
#   Keep minimal logging/comments, only for non-obvious logic. Do not change existing logging.
#   Handle errors and resources properly.
#   Stick to concise, essential code changes only.
#   Fix flake8 issues
