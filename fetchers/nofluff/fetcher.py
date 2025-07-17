import os
import re

from dotenv import load_dotenv
from playwright.async_api import async_playwright

from config import str_to_bool

load_dotenv()
NO_FLUFF_HEADLESS = str_to_bool(os.getenv("NO_FLUFF_HEADLESS", "false"))


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def clean_location(text: str) -> str:
    # Remove "+7" or similar suffixes and clean
    cleaned = re.sub(r"\+[\d]+$", "", text)
    return clean_text(cleaned)


async def fetch_nofluff_jobs(url: str) -> list[dict]:
    """
    Fetches full job data from NoFluffJobs.

    :param url: URL of the job listing page.
    :return: List of job dictionaries.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=NO_FLUFF_HEADLESS)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state("networkidle")

        job_cards = page.locator("a.posting-list-item")
        count = await job_cards.count()
        jobs = []

        for i in range(count):
            job = job_cards.nth(i)

            title = await job.locator(
                "h3.posting-title__position"
            ).text_content()
            company_name = await job.locator("h4.company-name").text_content()
            location_raw = await job.locator(
                "[data-cy='location on the job offer listing']"
            ).text_content()
            salary_raw = await job.locator(
                "[data-cy='salary ranges on the job offer listing']"
            ).text_content()
            skills = await job.locator(
                "nfj-posting-item-tiles span.posting-tag"
            ).all_text_contents()
            href = await job.get_attribute("href")

            jobs.append(
                {
                    "url": f"https://nofluffjobs.com{href}" if href else "",
                    "title": clean_text(title) if title else "",
                    "company_name": (
                        clean_text(company_name) if company_name else ""
                    ),
                    "skills": [clean_text(s) for s in skills],
                    "salary": clean_text(salary_raw) if salary_raw else "",
                    "location": (
                        clean_location(location_raw) if location_raw else ""
                    ),
                }
            )

        await browser.close()
        return jobs
