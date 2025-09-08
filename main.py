"""
Project coding rules:
- Use type hints and short docstrings (max 12 words)
- Minimal logging/comments, only for non-obvious logic
- Handle errors and resources properly
- Stick to concise, essential code changes only
"""

import os
import uvicorn
import asyncio
from src.api.fastapi_app import app


async def main() -> None:
    """Start FastAPI server with telegram bot and background jobs."""
    port = int(os.getenv("PORT", 8000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
