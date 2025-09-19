import re
from playwright.async_api import async_playwright, ViewportSize

from src.config import DOU_URL, DOU_HEADLESS, DOU_MAX_JOBS
from src.fetchers.dou.pagination import click_all_pagination_buttons
from logs.logger import logger
from src.utils.fetching.anti_block import get_random_user_agent, random_wait
from src.utils.fetching.fetcher_optimization import block_resources


def clean_text(text: str) -> str:
    """Normalize whitespace and remove non-breaking spaces."""
    if not isinstance(text, str):
        return ""
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


async def fetch_jobs() -> list[dict]:
    """Fetches full job data from DOU job listing page."""
    logger.info("-" * 60)
    logger.info(f"Starting to fetch DOU all_jobs through {DOU_URL}")

    all_jobs: list[dict] = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=DOU_HEADLESS)

            # Random User-Agent
            ua = get_random_user_agent()
            logger.info(f"User-agent: {ua}")
            page = await browser.new_page(
                viewport=ViewportSize(width=600, height=400)
            )
            await page.route("**/*", block_resources)

            await page.goto(DOU_URL)
            await page.wait_for_selector("ul.lt > li.l-vacancy")
            await click_all_pagination_buttons(page)

            job_cards = page.locator("ul.lt > li.l-vacancy")
            count = await job_cards.count()
            logger.info(f"Found {count} job listings.")

            for i in range(count):
                if len(all_jobs) >= DOU_MAX_JOBS:
                    logger.info(
                        f"Reached max job count of "
                        f"{DOU_MAX_JOBS}, stopping scraping."
                    )
                    break

                job = job_cards.nth(i)
                title_el = job.locator("div.title > a.vt")
                title = await title_el.text_content()
                url = await title_el.get_attribute("href")
                company_el = job.locator("div.title a.company")
                company = await company_el.text_content()
                location_el = job.locator("div.title span.cities")
                location = await location_el.text_content()

                clean_job = {
                    "title": clean_text(title) if title else "",
                    "url": clean_text(url) if url else "",
                    "company": clean_text(company) if company else "",
                    "location": clean_text(location) if location else "",
                }
                all_jobs.append(clean_job)
                logger.info(
                    f"{i+1:>3}. {clean_job['title']:<60} @ "
                    f"{clean_job.get('company', 'unknown')}"
                )

                # Anti-block delay
                await random_wait(0.5, 5.0)

        logger.info(
            f"Finished fetching all_jobs. Total all_jobs fetched:"
            f" {len(all_jobs)}"
        )
        return all_jobs

    except Exception as e:
        logger.exception(f"Error fetching jobs: {e}")
        return []

    finally:
        if browser:
            await browser.close()
