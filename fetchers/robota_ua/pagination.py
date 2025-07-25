import asyncio

from logs.logger import logger


async def click_next_page(page) -> bool:
    """Click the 'next' button once if available and wait for the new page to load.

    Returns True if clicked and page loaded, False if no next page.
    """
    next_button = await page.query_selector("a.side-btn.next.ng-star-inserted")
    if not next_button:
        logger.info("No 'next' button found. End of pages.")
        return False

    is_disabled = await next_button.get_attribute("disabled")
    if is_disabled:
        logger.info("'Next' button is disabled. No more pages.")
        return False

    old_url = page.url
    logger.info(f"Clicking next page button. Current URL: {old_url}")

    await next_button.click()

    # Wait for URL to change
    for _ in range(20):  # 20 * 0.5s = 10s
        await asyncio.sleep(0.5)
        new_url = page.url
        if new_url != old_url:
            logger.info(f"Page URL changed to: {new_url}")
            break
    else:
        logger.warning("URL did not change after clicking next.")
        return False

    # Wait for job cards to appear on the new page
    try:
        await page.wait_for_selector("a.card", timeout=10000)
        logger.info("Job cards loaded on next page.")
    except Exception:
        logger.warning("Job cards not found after clicking next page.")

    await page.wait_for_timeout(1000)  # optional buffer
    return True
