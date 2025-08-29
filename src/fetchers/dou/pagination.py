from playwright.async_api import Page

from logs.logger import logger
from src.utils.fetching.anti_block import random_wait


async def click_all_pagination_buttons(page: Page) -> None:
    """Click 'Load more' pagination button until it disappears."""
    logger.info("-" * 60)
    load_more_selector = "a:has-text('Більше вакансій')"

    try:
        while await page.locator(load_more_selector).is_visible():
            logger.info("Clicking 'Load more' to load more jobs...")
            await page.locator(load_more_selector).click()

            # Anti-block delay
            await random_wait(0.5, 5.0)
    except Exception as e:
        logger.warning(f"Error during pagination: {e}")


# fix paginatio na lot here to smal l user mlimit pagination cound how much did we get jobs etc.
