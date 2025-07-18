from logs.logger import logger


async def click_all_pagination_buttons(page):
    """
    Clicks the 'Load more' pagination button until it disappears.
    """
    logger.info("-" * 60)
    load_more_selector = "a:has-text('Більше вакансій')"

    try:
        while await page.locator(load_more_selector).is_visible():
            logger.info("Clicking 'Load more' to load more jobs...")
            await page.locator(load_more_selector).click()
            await page.wait_for_timeout(1000)  # wait 1s for content to load
    except Exception as e:
        logger.warning(f"Error during pagination: {e}")
