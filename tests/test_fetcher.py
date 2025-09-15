import pytest
from unittest.mock import AsyncMock, patch

from src.fetchers.pracuj.pracuj import run_fetch_and_save_jobs as fetch_pracuj


@pytest.mark.asyncio
async def test_pracuj_fetcher_basic() -> None:
    """Check fetcher returns list with title/company"""
    # Fast fake fetch
    with patch(
        "src.fetchers.pracuj.pracuj.fetch_pracuj_jobs", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = [{"title": "Python Dev", "company": "Acme"}]
        jobs = await fetch_pracuj()
        assert isinstance(jobs, list)
        if jobs:
            job = jobs[0]
            assert "title" in job
            assert "company" in job
