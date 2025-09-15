# tests/test_bot.py
import pytest
from unittest.mock import AsyncMock, patch
from src.telegram.telegram_bot import start_bot  # your real file

pytestmark = pytest.mark.asyncio


async def test_start_bot_calls_notify_admin_startup():
    with patch(
        "src.telegram.telegram_bot.notify_admin_startup",
        new_callable=AsyncMock,
    ) as mock_notify, patch(
        "src.telegram.telegram_bot.dp.start_polling", new_callable=AsyncMock
    ):
        await start_bot()
        mock_notify.assert_called_once()
