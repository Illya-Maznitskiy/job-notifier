import pytest
from unittest.mock import AsyncMock, patch

from sqlalchemy import CursorResult

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
    # Create an AsyncMock for the session
    mock_session = AsyncMock()

    # The result of `session.execute()` is a mock result object
    mock_result = AsyncMock(spec=CursorResult)
    # The `scalar()` method on the result object is async,
    # so it must return an awaitable
    # We set its return_value to the value we want to simulate
    mock_result.scalar.return_value = 1

    # Now, we set up the `execute` method of the session mock
    # to return our mock result object
    mock_session.execute.return_value = mock_result

    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_session

    with patch("src.db.db.AsyncSessionLocal", return_value=mock_context):
        await test_connection()
        mock_session.execute.assert_called_once()
