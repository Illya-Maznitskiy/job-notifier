import asyncio
from typing import Tuple, Dict, Any, List

from playwright.async_api import (
    async_playwright,
    Browser,
    Page,
    ElementHandle,
    Playwright,
)
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
    Error as PlaywrightError,
)

from src.config import JUST_JOIN_HEADLESS, JUST_JOIN_URL
from src.fetchers.justjoin.pagination import (
    scroll_and_fetch_jobs,
)
from logs.logger import logger
from src.utils.fetching.anti_block import get_random_user_agent

from src.utils.fetching.fetcher_optimization import block_resources


async def setup_page(playwright: Playwright, url: str) -> Tuple[Browser, Page]:
    """Launch browser, open page, handle cookies, and wait for offers."""
    logger.info("-" * 60)
    logger.info("Starting setup page")

    try:
        browser: Browser = await playwright.chromium.launch(
            headless=JUST_JOIN_HEADLESS
        )

        # Random User-Agent
        ua = get_random_user_agent()
        logger.info(f"User-agent: {ua}")
        page: Page = await browser.new_page(user_agent=ua)

        await page.route("**/*", block_resources)
        await page.goto(url)

        try:
            await page.click("#cookiescript_reject", timeout=30000)
            logger.info("Cookie consent rejected.")
        except PlaywrightTimeoutError:
            logger.debug("No cookie popup found or already handled.")

        await page.wait_for_selector("a.offer-card", timeout=10000)
        return browser, page

    except Exception as err:
        logger.error(f"Error setting up page: {err}")
        raise


async def parse_job_offer(offer: ElementHandle) -> Dict[str, Any]:
    """
    Extract job details asynchronously from a job offer element.
    """
    title_el = await offer.query_selector("h3")
    title = (await title_el.text_content()).strip() if title_el else "Unknown"

    href = await offer.get_attribute("href")
    job_url = f"https://justjoin.it{href}" if href else None

    company_el = await offer.query_selector(
        "p.MuiTypography-root.MuiTypography-body1"
    )
    company = (
        (await company_el.text_content()).strip() if company_el else "Unknown"
    )

    salary_els = await offer.query_selector_all("div.mui-18ypp16 span")
    if len(salary_els) >= 2:
        min_salary_text = await salary_els[0].text_content()
        max_salary_text = await salary_els[1].text_content()
        currency_el = await offer.query_selector(
            "div.mui-18ypp16 span.mui-1m61siv"
        )
        currency_text = (
            await currency_el.text_content() if currency_el else None
        )

        try:
            min_salary = int(min_salary_text.replace(" ", ""))
            max_salary = int(max_salary_text.replace(" ", ""))
            average_salary = (min_salary + max_salary) // 2
            salary = str(average_salary)
            currency = currency_text.strip() if currency_text else None
        except ValueError:
            salary = None
            currency = None
    else:
        salary = None
        currency = None

    location_el = await offer.query_selector("span.mui-1o4wo1x")
    location = (
        (await location_el.text_content()).strip() if location_el else None
    )

    skill_els = await offer.query_selector_all(
        "div.skill-tag-1 div.mui-jikuwi"
    )
    skills = [
        s.strip()
        for s in (await asyncio.gather(*[s.text_content() for s in skill_els]))
    ]

    return {
        "title": title.strip() if title else "Unknown",
        "url": job_url,
        "company": company.strip() if company else "Unknown",
        "salary": salary.strip() if salary else None,
        "currency": currency.strip() if currency else None,
        "location": location.strip() if location else None,
        "skills": [s.strip() for s in skills],
    }


async def fetch_jobs() -> List[Dict[str, Any]]:
    """
    Launch browser and scrape job offers from target URL asynchronously.
    """
    url = JUST_JOIN_URL

    logger.info("-" * 60)
    logger.info(f"Starting fetch_jobs for URL: {url}")

    try:
        async with async_playwright() as p:
            browser, page = await setup_page(p, url)

            # Scroll and fetch incrementally
            results = await scroll_and_fetch_jobs(page)

            await browser.close()
            logger.info("Browser closed. Finished fetching jobs.")
            return results

    except PlaywrightTimeoutError as timeout_err:
        logger.error(f"Timeout while fetching jobs: {timeout_err}")
        return []
    except PlaywrightError as pw_err:
        logger.error(f"Playwright error: {pw_err}")
        return []
