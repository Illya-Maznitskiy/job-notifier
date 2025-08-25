import asyncio

from logs.logger import logger


async def click_next_page(page) -> bool:
    """Click the (current_page + 1) pagination button if available.

    Returns True if clicked and page loaded, False otherwise.
    """
    logger.info("Looking for current page in paginator.")
    current_link = await page.query_selector("div.paginator a.active")
    if not current_link:
        logger.warning("Could not find current active page link.")
        return False

    current_text = await current_link.inner_text()
    try:
        current_page = int(current_text.strip())
    except ValueError:
        logger.error(f"Failed to parse current page number: {current_text}")
        return False

    next_page = current_page + 1
    logger.info(f"Current page: {current_page}, looking for page: {next_page}")

    next_page_selector = f'div.paginator a:has-text("{next_page}")'
    next_link = await page.query_selector(next_page_selector)

    if not next_link:
        logger.info(f"No link found for page {next_page}. End of pagination.")
        return False

    old_url = page.url
    logger.info(f"Clicking page {next_page}. Current URL: {old_url}")
    await next_link.click()

    # Wait for URL to change
    for _ in range(20):  # 20 * 0.5s = 10s
        await asyncio.sleep(0.5)
        new_url = page.url
        if new_url != old_url:
            logger.info(f"Page URL changed to: {new_url}")
            break
    else:
        logger.warning("URL did not change after clicking next page.")
        return False

    try:
        await page.wait_for_selector("a.card", timeout=10000)
        logger.info("Job cards loaded on next page.")
    except Exception:
        logger.warning("Job cards not found after clicking next page.")

    # Delay to ensure page has fully settled before next operation
    await page.wait_for_timeout(1000)
    return True
