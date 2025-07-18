import os
import re
from dotenv import load_dotenv
from playwright.async_api import async_playwright

from fetchers.dou.pagination import click_all_pagination_buttons
from logs.logger import logger
from utils.convert_bool import str_to_bool

load_dotenv()
DOU_HEADLESS = str_to_bool(os.getenv("DOU_HEADLESS", "false"))
DOU_URL = os.getenv("DOU_URL", "https://jobs.dou.ua/vacancies/")


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def clean_location(text: str) -> str:
    return clean_text(text)


async def fetch_jobs() -> list[dict]:
    """
    Fetches full job data from DOU job listing page.

    :return: List of job dictionaries.
    """
    logger.info("-" * 60)
    logger.info("Starting to fetch DOU jobs...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=DOU_HEADLESS)
        page = await browser.new_page()
        await page.goto(DOU_URL)
        await page.wait_for_selector("ul.lt > li.l-vacancy")

        await click_all_pagination_buttons(page)

        job_cards = page.locator("ul.lt > li.l-vacancy")
        count = await job_cards.count()
        jobs = []

        logger.info(f"Found {count} job listings.")

        for i in range(count):
            job = job_cards.nth(i)

            title_el = job.locator("div.title > a.vt")
            title = await title_el.text_content()
            url = await title_el.get_attribute("href")

            company_el = job.locator("div.title a.company")
            company_name = await company_el.text_content()

            location_el = job.locator("div.title span.cities")
            location = await location_el.text_content()

            clean_job = {
                "title": clean_text(title) if title else "",
                "url": clean_text(url) if url else "",
                "company_name": (
                    clean_text(company_name) if company_name else ""
                ),
                "location": clean_location(location) if location else "",
            }

            jobs.append(clean_job)

            logger.info(
                f"{i+1}: '{clean_job['title']}' at '{clean_job['company_name']}'"
            )

        await browser.close()

    logger.info(f"Finished fetching jobs. Total jobs fetched: {len(jobs)}")
    return jobs
