from typing import Dict, Any, Union, List

from playwright.async_api import async_playwright, ViewportSize
from tqdm.asyncio import tqdm_asyncio

from src.config import BULLDOG_MAX_JOBS, BULLDOG_HEADLESS
from src.fetchers.bulldog.pagination import (
    bulldog_pages,
    get_bulldog_max_pages,
)
from logs.logger import logger
from src.utils.fetching.anti_block import (
    get_random_user_agent,
    random_wait,
)
from src.utils.fetching.fetcher_optimization import block_resources


async def extract_bulldog_job(item: Any) -> Dict[str, Union[str, List[str]]]:
    """Extract job info from Bulldog job element safely."""
    job: Dict[str, Union[str, List[str]]] = {}

    try:
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

        salary_el = await item.query_selector(
            "div.JobListItem_item__salary__OIin6"
        )
        if salary_el:
            salary = await salary_el.text_content()
            if salary:
                job["salary"] = salary.strip()

        # Collect all skills, stripping whitespace
        skill_elements = await item.query_selector_all(
            "div.JobListItem_item__tags__POZkk span"
        )
        skills = [await el.text_content() for el in skill_elements]
        if skills:
            job["skills"] = [s.strip() for s in skills]

    except Exception as err:
        logger.exception(f"Failed to extract job: {err}")

    return job


async def fetch_bulldog_jobs() -> List[Dict[str, Any]]:
    """Fetch jobs from Bulldogjob site asynchronously."""
    all_jobs: List[Dict[str, Any]] = []

    try:
        logger.info("-" * 60)
        logger.info("Launching browser for Bulldogjob scraping")

        async with async_playwright() as p:
            launch_args: Dict[str, Any] = {"headless": BULLDOG_HEADLESS}
            browser = await p.chromium.launch(**launch_args)

            # Random User-Agent
            ua = get_random_user_agent()
            logger.info(f"User-agent: {ua}")
            page = await browser.new_page(
                viewport=ViewportSize(width=600, height=400)
            )
            await page.route("**/*", block_resources)

            max_pages = await get_bulldog_max_pages(page)

            # Loop through multiple pages
            for url in bulldog_pages(start=1, end=max_pages):
                logger.info(f"Fetching Bulldog page: {url}")
                await page.goto(url)
                await page.wait_for_selector(
                    "a.JobListItem_item__fYh8y", timeout=5000
                )
                job_items = await page.query_selector_all(
                    "a.JobListItem_item__fYh8y"
                )

                if not job_items:
                    logger.info("No job items found on this page.")
                    continue

                for i, item in enumerate(
                    tqdm_asyncio(
                        job_items, desc="Fetching jobs", mininterval=120.0
                    ),
                    1,
                ):
                    # Jobs limit
                    if len(all_jobs) >= BULLDOG_MAX_JOBS:
                        logger.info(
                            f"Reached max job count of {BULLDOG_MAX_JOBS}, "
                            f"stopping scraping."
                        )
                        break

                    job = await extract_bulldog_job(item)
                    if "title" in job and "url" in job:
                        all_jobs.append(job)
                        logger.debug(
                            f"{len(all_jobs):>3}. {job['title']:<60} @ "
                            f"{job.get('company', 'unknown')}"
                        )
                    else:
                        logger.warning(
                            f"Skipped job #{i} due to missing title or URL"
                        )

                    # Anti-block delay
                    await random_wait(0.5, 5.0)

                if len(all_jobs) >= BULLDOG_MAX_JOBS:
                    break

            await browser.close()
            logger.info(f"Scraping done. Total jobs fetched: {len(all_jobs)}")

    except Exception as err:
        logger.exception(f"Error fetching Bulldog jobs: {err}")

    return all_jobs
