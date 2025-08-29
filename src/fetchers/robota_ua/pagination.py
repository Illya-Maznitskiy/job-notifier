from playwright.async_api import Page

from logs.logger import logger


async def click_next_page(page: Page) -> bool:
    """Clicks the next page pagination button."""
    current_link = await page.query_selector("div.paginator a.active")
    if not current_link:
        logger.warning("No active page link found.")
        return False

    current_text = await current_link.inner_text()
    try:
        current_page = int(current_text.strip())
    except ValueError:
        logger.error(f"Failed to parse page number: {current_text}")
        return False

    next_page = current_page + 1
    logger.info(f"Current page: {current_page}, looking for page: {next_page}")

    next_page_selector = f'div.paginator a:has-text("{next_page}")'
    next_link = await page.query_selector(next_page_selector)

    if not next_link:
        logger.info("End of pagination.")
        return False

    old_url = page.url
    logger.info(f"Clicking page {next_page}. Current URL: {old_url}")
    await next_link.click()

    try:
        await page.wait_for_url(lambda url: url != old_url, timeout=10000)
        await page.wait_for_selector("a.card", timeout=10000)
    except Exception as e:
        logger.warning(f"Navigation or content load failed: {e}")
        return False

    return True
