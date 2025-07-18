import os
import re

from dotenv import load_dotenv
from playwright.async_api import async_playwright

from logs.logger import logger
from utils.convert_bool import str_to_bool


load_dotenv()
PRACUJ_HEADLESS = str_to_bool(os.getenv("PRACUJ_HEADLESS", "false"))


async def accept_cookies_if_present(page):
    logger.info("-" * 60)
    try:
        # Wait for the cookie button to appear (if it does)
        await page.locator("button[data-test='button-submitCookie']").click(
            timeout=3000
        )
        logger.info("Accepted cookies")
    except Exception:
        # No cookie prompt found
        logger.debug("No cookie prompt found, continuing")


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


async def fetch_pracuj_jobs(url: str) -> list[dict]:
    logger.info("-" * 60)
    logger.info(f"Starting job fetch from: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=PRACUJ_HEADLESS)
        page = await browser.new_page()
        await page.goto(url)
        await accept_cookies_if_present(page)
        await page.mouse.wheel(0, 300)  # simulate scroll

        await page.wait_for_selector(
            "h2[data-test='offer-title']", timeout=10000
        )
        await page.mouse.wheel(0, 300)  # simulate scroll

        cards = page.locator(
            "div[data-test='positioned-offer'], div[data-test='default-offer']"
        ).filter(has_not=page.locator("div[data-test='section-ad-container']"))

        await page.wait_for_timeout(500)
        count = await cards.count()
        logger.info(f"Found {count} job cards")
        jobs = []

        async def safe_text(locator, field_name=""):
            try:
                return await locator.text_content(timeout=2000) or ""
            except Exception as e:
                if "offer-salary" in field_name:
                    logger.debug("No salary info")
                else:
                    logger.debug(f"Failed to get text content: {e}")
                return ""

        async def safe_attr(locator, attr):
            try:
                return await locator.get_attribute(attr, timeout=2000) or ""
            except Exception as e:
                logger.debug(f"Failed to get attribute '{attr}': {e}")
                return ""

        for i in range(count):
            logger.debug(f"Processing job {i + 1}/{count}")
            job = cards.nth(i)

            title = await safe_text(job.locator("h2[data-test='offer-title']"))
            salary = await safe_text(
                job.locator("span[data-test='offer-salary']"),
                field_name="offer-salary",
            )
            company = await safe_text(
                job.locator("h3[data-test='text-company-name']")
            )
            city = await safe_text(job.locator("h4[data-test='text-region']"))
            work_fmt = await safe_text(
                job.locator("ul.tiles_bfrsaoj li").first
            )

            link = await safe_attr(
                job.locator(
                    "a[data-test='link-offer-title'], "
                    "a[data-test='link-offer']"
                ).first,
                "href",
            )

            jobs.append(
                {
                    "url": link,
                    "title": clean_text(title),
                    "company": clean_text(company),
                    "salary": clean_text(salary),
                    "city": clean_text(city),
                    "work_format": clean_text(work_fmt),
                }
            )
        await browser.close()
    logger.info(f"Finished fetching jobs, total collected: {len(jobs)}")
    return jobs
