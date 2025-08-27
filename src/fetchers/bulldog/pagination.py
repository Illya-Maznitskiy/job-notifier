from logs.logger import logger
from src.config import BULLDOG_URL


async def get_bulldog_max_pages(page) -> int:
    """Get max BulldogJob pages from pagination element on first page."""
    await page.goto(BULLDOG_URL)
    await page.wait_for_selector(
        "li.w-10.h-10.mx-1.rounded-full"
    )  # pagination items
    page_items = await page.query_selector_all(
        "li.w-10.h-10.mx-1.rounded-full"
    )

    max_page = 1
    for item in page_items:
        text = await item.text_content()
        if text and text.isdigit():
            num = int(text.strip())
            if num > max_page:
                max_page = num
    logger.info(f"Detected {max_page} pages on BulldogJob")
    return max_page


def bulldog_pages(start: int = 1, end: int = 5) -> list[str]:
    """Generate BulldogJob page URLs for pagination."""
    pages = [
        f"https://bulldogjob.com/companies/jobs/s/page,{i}"
        for i in range(start, end + 1)
    ]
    logger.info(f"Generated {len(pages)} BulldogJob page URLs: {pages}")
    return pages
