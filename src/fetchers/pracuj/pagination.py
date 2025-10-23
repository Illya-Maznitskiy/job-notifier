from typing import List, Dict

from playwright.async_api import Page
from playwright.async_api import Error as PlaywrightError

from logs.logger import logger
from src.utils.fetching.anti_block import random_wait


async def paginate_jobs(page: Page, max_jobs: int) -> List[Dict[str, str]]:
    """Fetch jobs through pagination, up to max_jobs."""
    # fix circular import
    from src.fetchers.pracuj.fetcher import fetch_jobs_on_page

    all_jobs: List[Dict[str, str]] = []
    page_number = 1

    while True:
        # Jobs limit
        if len(all_jobs) >= max_jobs:
            logger.info(
                f"Reached max job count of {max_jobs}, stopping pagination."
            )
            break

        jobs_on_page = await fetch_jobs_on_page(page)
        all_jobs.extend(jobs_on_page)
        logger.info(
            f"Collected {len(all_jobs)} jobs so far after page {page_number}."
        )

        # Anti-block delay
        await random_wait(0.5, 10.0)

        next_button = page.locator(
            "button[data-test='bottom-pagination-button-next']"
        )
        try:
            if await next_button.is_enabled(timeout=2000):
                logger.info(
                    f"Next page button enabled, going to page "
                    f"{page_number + 1}."
                )
                await next_button.click()
                await page.wait_for_timeout(3000)
                await page.wait_for_selector(
                    "div[data-test='positioned-offer'], div["
                    "data-test='default-offer']",
                    timeout=10000,
                )
                await page.wait_for_timeout(300)
                page_number += 1
            else:
                logger.info("Next page button disabled, ending pagination.")
                break
        except PlaywrightError:
            logger.info("Next page button not clickable, ending pagination.")
            break

    return all_jobs
