import os
from typing import Dict, Any

from dotenv import load_dotenv
from playwright.async_api import async_playwright

from src.config import BULLDOG_MAX_JOBS
from src.utils.convert_bool import str_to_bool
from logs.logger import logger
from src.utils.fetching.anti_block import (
    get_random_proxy,
    get_random_user_agent,
    random_wait,
)
from src.utils.fetching.fetcher_optimization import block_resources


load_dotenv()

BULLDOG_URL = os.getenv("BULLDOG_URL", "https://bulldogjob.com/companies/jobs")
BULLDOG_HEADLESS = str_to_bool(os.getenv("BULLDOG_HEADLESS", "true"))


async def extract_bulldog_job(item) -> dict:
    job = {}

    title_el = await item.query_selector("h3")
    if title_el:
        title = await title_el.text_content()
        if title:
            job["title"] = title.strip()

    url_el = await item.get_attribute("href")
    if url_el:
        job["url"] = url_el.strip()

    company_el = await item.query_selector("div.uppercase")
    if company_el:
        company = await company_el.text_content()
        if company:
            job["company"] = company.strip()

    location_el = await item.query_selector(
        "div.JobListItem_item__details__sg4tk span.text-xs"
    )
    if location_el:
        location = await location_el.text_content()
        if location:
            job["location"] = location.strip()

    level_els = await item.query_selector_all(
        "div.JobListItem_item__details__sg4tk span"
    )
    for el in level_els:
        text = (await el.text_content()).lower()
        if "junior" in text or "mid" in text or "senior" in text:
            job["level"] = text.strip()
            break

    salary_el = await item.query_selector(
        "div.JobListItem_item__salary__OIin6"
    )
    if salary_el:
        salary = await salary_el.text_content()
        if salary:
            job["salary"] = salary.strip()

    skill_elements = await item.query_selector_all(
        "div.JobListItem_item__tags__POZkk span"
    )
    skills = [await el.text_content() for el in skill_elements]
    if skills:
        job["skills"] = [s.strip() for s in skills]

    return job


async def fetch_bulldog_jobs():
    logger.info("-" * 60)
    logger.info("Launching browser for Bulldogjob scraping")

    async with async_playwright() as p:
        launch_args: Dict[str, Any] = {"headless": BULLDOG_HEADLESS}
        browser = await p.chromium.launch(**launch_args)

        # Random User-Agent
        ua = get_random_user_agent()
        logger.info(f"User-agent: {ua}")
        page = await browser.new_page(user_agent=ua)

        await page.route("**/*", block_resources)

        all_jobs = []

        logger.info(f"Fetching Bulldog page: {BULLDOG_URL}")
        await page.goto(BULLDOG_URL)

        await page.wait_for_selector("a.JobListItem_item__fYh8y", timeout=5000)
        job_items = await page.query_selector_all("a.JobListItem_item__fYh8y")

        if not job_items:
            logger.info("No job items found on the page.")
        else:
            for i, item in enumerate(job_items, start=1):
                if len(all_jobs) >= BULLDOG_MAX_JOBS:
                    logger.info(
                        f"Reached max job count of {BULLDOG_MAX_JOBS}, stopping scraping."
                    )
                    break

                job = await extract_bulldog_job(item)
                if "title" in job and "url" in job:
                    all_jobs.append(job)
                    logger.info(
                        f"{len(all_jobs):>3}. {job['title']:<60} @ {job.get('company', 'unknown')}"
                    )

                else:
                    logger.warning(
                        f"Skipped job #{i} due to missing title or URL"
                    )

                # Anti-block delay
                await random_wait(0.5, 5.0)

        await browser.close()
        logger.info(f"Scraping done. Total jobs fetched: {len(all_jobs)}")
        return all_jobs
