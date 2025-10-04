from playwright.async_api import Page

from logs.logger import logger
from src.config import DOU_MAX_JOBS
from src.utils.fetching.anti_block import random_wait


async def click_all_pagination_buttons(page: Page) -> None:
    """Click 'Load more' until no more jobs or max_jobs reached."""
    logger.info("-" * 60)
    load_more_selector = "a:has-text('Більше вакансій')"
    job_selector = "li.l-vacancy"

    try:
        while await page.locator(load_more_selector).is_visible():
            jobs_count = await page.locator(job_selector).count()
            logger.debug(f"Current job count: {jobs_count}")

            # Stop if we've reached max_jobs
            if jobs_count >= DOU_MAX_JOBS:
                logger.info(f"Reached max_jobs limit: {DOU_MAX_JOBS}")
                break

            logger.debug("Clicking 'Load more' to load more jobs...")
            await page.locator(load_more_selector).click()

            # Anti-block delay
            await random_wait(0.5, 5.0)

        # Final job count
        final_count = await page.locator(job_selector).count()
        logger.info(f"Total jobs loaded: {final_count}")

    except Exception as e:
        logger.warning(f"Error during pagination: {e}")
