import asyncio
import re
from typing import Dict, List
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from playwright.async_api import async_playwright, Page, Locator
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
    Error as PlaywrightError,
)

from logs.logger import logger
from src.config import PRACUJ_HEADLESS, PRACUJ_MAX_JOBS
from src.utils.fetching.anti_block import get_random_user_agent, random_wait
from src.utils.fetching.fetcher_optimization import block_pracuj_resources


async def accept_cookies_if_present(page: Page) -> None:
    """Accept cookies if popup appears."""
    logger.info("-" * 60)
    await asyncio.sleep(1)

    try:
        await page.locator("button[data-test='button-submitCookie']").click(
            timeout=3000
        )
        logger.info("Accepted cookies using data-test locator")
        return
    except (PlaywrightTimeoutError, PlaywrightError):
        logger.info("First cookie button not found")

    try:
        await page.get_by_role("button", name="OK, rozumiem").click(
            timeout=3000
        )
        logger.info(
            "Accepted cookies using fallback locator for 'OK, rozumiem'"
        )
    except (PlaywrightTimeoutError, PlaywrightError):
        logger.debug("Second cookie button not found, continuing")


def clean_text(text: str) -> str:
    """Normalize whitespace and remove non-breaking spaces."""
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


async def safe_text(locator: Locator) -> str:
    """Return text content safely from locator."""
    try:
        return await locator.text_content(timeout=2000) or ""
    except (PlaywrightTimeoutError, PlaywrightError):
        return ""


async def safe_attr(locator: Locator, attr: str) -> str:
    """Return attribute safely from locator."""
    try:
        return await locator.get_attribute(attr, timeout=3000) or ""
    except (PlaywrightTimeoutError, PlaywrightError):
        return ""


def remove_tracking_params(url: str) -> str:
    """Remove tracking query parameters from URL."""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    tracking_keys = ["s", "ref", "searchId"]
    for key in tracking_keys:
        query_params.pop(key, None)

    cleaned_query = urlencode(query_params, doseq=True)
    cleaned_url = parsed_url._replace(query=cleaned_query)

    return str(urlunparse(cleaned_url))


async def extract_url_from_expanded_form(job: Locator) -> str:
    """Get first location URL from expanded job form."""
    try:
        expand_button = job.locator(
            "div[title^='Zobacz ofertę'], span[role='button']"
        )
        if await expand_button.count() > 0:
            await expand_button.first.click()
            await asyncio.sleep(0.5)

        location_links = job.locator("a[data-test='link-offer']")
        if await location_links.count() > 0:
            href = await location_links.nth(0).get_attribute("href")
            if href:
                return href
    except (PlaywrightTimeoutError, PlaywrightError) as e:
        logger.debug(f"Failed to get URL from expanded form: {e}")

    return ""


async def extract_job_data(
    job: Locator, page: Page, index: int
) -> Dict[str, str]:
    """Extract data for a single job card."""
    await job.scroll_into_view_if_needed()
    await page.wait_for_timeout(300)

    title = await safe_text(job.locator("h2[data-test='offer-title']"))
    salary = await safe_text(job.locator("span[data-test='offer-salary']"))
    company = await safe_text(job.locator("h3[data-test='text-company-name']"))
    city = await safe_text(job.locator("h4[data-test='text-region']"))
    work_fmt = await safe_text(job.locator("ul.tiles_bfrsaoj li").first)

    link = await safe_attr(
        job.locator(
            "a[data-test='link-offer-title'], a[data-test='link-offer']"
        ).first,
        "href",
    )

    if not link:
        anchors = job.locator("a")
        for j in range(await anchors.count()):
            href = await safe_attr(anchors.nth(j), "href")
            if href and "/oferta/" in href:
                link = href
                break

    if not link:
        link = await extract_url_from_expanded_form(job)

    if link:
        link = remove_tracking_params(link)
    else:
        logger.warning(
            f"No valid job link found for job {index + 1} - Title: {title}"
        )

    return {
        "url": link or "",
        "title": clean_text(title),
        "company": clean_text(company),
        "salary": clean_text(salary),
        "city": clean_text(city),
        "work_format": clean_text(work_fmt),
    }


async def fetch_jobs_on_page(page: Page) -> List[Dict[str, str]]:
    """Fetch all job cards on the current page."""
    cards = page.locator(
        "div[data-test='positioned-offer'], div[data-test='default-offer']"
    ).filter(has_not=page.locator("div[data-test='section-ad-container']"))

    count = await cards.count()
    logger.info(f"Found {count} job cards on page")
    return await asyncio.gather(
        *(extract_job_data(cards.nth(i), page, i) for i in range(count))
    )


async def fetch_pracuj_jobs(url: str) -> List[Dict[str, str]]:
    """Fetch job listings from Pracuj with pagination, cookies handling, and tracking removal."""
    logger.info("-" * 60)
    logger.info(f"Starting job fetch from: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=PRACUJ_HEADLESS)

        # Random User-Agent
        ua = get_random_user_agent()
        logger.info(f"User-agent: {ua}")
        page = await browser.new_page(user_agent=ua)
        await block_pracuj_resources(page)
        await page.goto(url)
        await page.wait_for_timeout(3000)
        await accept_cookies_if_present(page)

        all_jobs: List[Dict[str, str]] = []
        page_number = 1

        while True:
            # Jobs limit
            if len(all_jobs) >= PRACUJ_MAX_JOBS:
                logger.info(
                    f"Reached max job count of {PRACUJ_MAX_JOBS}, stopping scraping."
                )
                break

            try:
                await page.wait_for_selector(
                    "h2[data-test='offer-title']", timeout=10000
                )
            except PlaywrightTimeoutError:
                logger.warning(
                    f"No job listings found on page {page_number}, stopping."
                )
                break

            jobs_on_page = await fetch_jobs_on_page(page)
            all_jobs.extend(jobs_on_page)

            # Anti-block delay
            await random_wait(0.5, 5.0)

            next_button = page.locator(
                "button[data-test='bottom-pagination-button-next']"
            )
            try:
                if await next_button.is_enabled(timeout=2000):
                    logger.info(
                        f"Next page button enabled, continuing pagination."
                    )
                    await next_button.click()
                    await page.wait_for_timeout(3000)
                    await page.wait_for_selector(
                        "div[data-test='positioned-offer'], div[data-test='default-offer']",
                        timeout=10000,
                    )
                    await page.wait_for_timeout(300)
                    page_number += 1
                else:
                    logger.info(
                        "Next page button disabled, ending pagination."
                    )
                    break
            except PlaywrightError:
                logger.info(
                    "Next page button not clickable, ending pagination."
                )
                break

        await browser.close()

    logger.info(
        f"Finished fetching all_jobs, total collected: {len(all_jobs)}"
    )
    return all_jobs
