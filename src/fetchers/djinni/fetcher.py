from playwright.async_api import async_playwright

from typing import Dict, List, Union

from src.config import DJINNI_HEADLESS, DJINNI_URL, DJINNI_MAX_JOBS
from src.fetchers.djinni.pagination import build_paginated_url
from logs.logger import logger
from src.utils.fetching.anti_block import get_random_user_agent, random_wait
from src.utils.fetching.fetcher_optimization import block_resources


async def extract_job_data(item) -> Dict[str, Union[str, List[str]]]:
    """Extract Djinni job info safely."""
    job: Dict[str, Union[str, List[str]]] = {}

    try:
        title_el = await item.query_selector("h2 a.job-item__title-link")
        if title_el:
            title = await title_el.text_content()
            href = await title_el.get_attribute("href")
            if title:
                job["title"] = title.strip()
            if href:
                job["url"] = f"https://djinni.co{href}"

        company_el = await item.query_selector(
            "a.text-body.js-analytics-event"
        )
        job["company"] = (
            (await company_el.text_content()).strip()
            if company_el and await company_el.text_content()
            else "unknown"
        )

        location_el = await item.query_selector("span.location-text")
        if location_el:
            loc = await location_el.text_content()
            if loc:
                job["location"] = loc.strip()

        salary_el = await item.query_selector(".job-item__salary")
        if salary_el:
            salary_text = (await salary_el.text_content() or "").strip()
            if salary_text:
                parts = salary_text.split()
                if parts:
                    job["salary"] = parts[0]
                    if len(parts) > 1:
                        job["currency"] = " ".join(parts[1:])

        skills_elements = await item.query_selector_all(".job-item__tags span")
        skills: List[str] = [
            s.strip()
            for s in [await el.text_content() for el in skills_elements]
            if s
        ]
        if skills:
            job["skills"] = skills

    except Exception as err:
        logger.exception(f"Unhandled error in main: {err}")

    return job


async def fetch_jobs() -> List[Dict]:
    """Fetch jobs from Djinni with pagination."""
    logger.info("-" * 60)
    logger.info("Starting browser and navigating to Djinni base URL")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=DJINNI_HEADLESS)

            # Random User-Agent
            ua = get_random_user_agent()
            logger.info(f"User-agent: {ua}")
            page = await browser.new_page(user_agent=ua)
            await page.route("**/*", block_resources)

            all_jobs: List[Dict] = []
            page_num = 1

            while True:
                paginated_url = build_paginated_url(DJINNI_URL, page_num)
                logger.info(f"Fetching page {page_num}: {paginated_url}")
                await page.goto(paginated_url)

                try:
                    await page.wait_for_selector(
                        "ul.list-unstyled > li", timeout=30000
                    )
                except TimeoutError:
                    logger.info("No job listings found. Stopping pagination.")
                    break

                job_items = await page.query_selector_all(
                    "ul.list-unstyled > li"
                )
                if not job_items:
                    logger.info("No job listings found. Stopping pagination.")
                    break

                for i, item in enumerate(job_items, start=1):
                    if len(all_jobs) >= DJINNI_MAX_JOBS:
                        logger.info(
                            f"Reached max job count of {DJINNI_MAX_JOBS}, stopping scraping."
                        )
                        break

                    job = await extract_job_data(item)
                    if "title" in job and "url" in job:
                        all_jobs.append(job)
                        logger.info(
                            f"{len(all_jobs):>3}. {job['title']:<60} @ {job.get('company', 'unknown')}"
                        )
                    else:
                        logger.warning(
                            f"Skipped job #{i} due to missing title or url"
                        )

                    # Anti-block delay
                    await random_wait(0.5, 5.0)

                if len(all_jobs) >= DJINNI_MAX_JOBS:
                    break

                # Pagination check
                pagination_items = await page.query_selector_all(
                    "ul.pagination li.page-item a.page-link"
                )
                page_numbers = [
                    int(await item.text_content())
                    for item in pagination_items
                    if (await item.text_content())
                    and (await item.text_content()).strip().isdigit()
                ]
                logger.info(f"Pagination buttons found: {page_numbers}")

                if (page_num + 1) not in page_numbers:
                    logger.info(
                        f"No button for page {page_num + 1}. Stopping pagination."
                    )
                    break

                page_num += 1

            await browser.close()
            logger.info(f"Browser closed. Total jobs fetched: {len(all_jobs)}")
            return all_jobs

    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        return []
