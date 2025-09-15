# tests/test_db.py
import pytest
from unittest.mock import AsyncMock, patch
from src.db.db import get_session, test_connection

pytestmark = pytest.mark.asyncio


async def test_get_session_yields_session():
    mock_session = AsyncMock()
    # Patch AsyncSessionLocal so that its __aenter__ returns mock_session
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_session

    with patch("src.db.db.AsyncSessionLocal", return_value=mock_context):
        async for session in get_session():
            assert session == mock_session  # now passes


async def test_test_connection_runs_without_error():
    mock_session = AsyncMock()
    mock_session.execute.return_value.scalar.return_value = 1

    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_session

    with patch("src.db.db.AsyncSessionLocal", return_value=mock_context):
        await test_connection()
        mock_session.execute.assert_called_once()
