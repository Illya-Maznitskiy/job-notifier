import os

from dotenv import load_dotenv
from playwright.async_api import async_playwright

from utils.convert_bool import str_to_bool
from fetchers.djinni.pagination import build_paginated_url
from logs.logger import logger
from utils.fetcher_optimization import block_resources

load_dotenv()


DJINNI_URL = os.getenv("DJINNI_URL")
DJINNI_HEADLESS = str_to_bool(os.getenv("DJINNI_HEADLESS", "false"))


async def extract_job_data(item) -> dict:
    job = {}

    title_el = await item.query_selector("h2 a.job-item__title-link")
    if title_el:
        title = await title_el.text_content()
        href = await title_el.get_attribute("href")
        if title:
            job["title"] = title.strip()
        if href:
            job["url"] = f"https://djinni.co{href}"

    company_el = await item.query_selector("a.text-body.js-analytics-event")
    if company_el:
        company = await company_el.text_content()
        if company:
            job["company"] = company.strip()

    location_el = await item.query_selector("span.location-text")
    if location_el:
        location = await location_el.text_content()
        if location:
            job["location"] = location.strip()

    salary_el = await item.query_selector(".job-item__salary")
    if salary_el:
        salary_text = (await salary_el.text_content()) or ""
        salary_text = salary_text.strip()
        if salary_text:
            parts = salary_text.split()
            if parts:
                job["salary"] = parts[0]
                if len(parts) > 1:
                    job["currency"] = " ".join(parts[1:])

    skills_elements = await item.query_selector_all(".job-item__tags span")
    skills = []
    for skill_el in skills_elements:
        skill = await skill_el.text_content()
        if skill:
            skills.append(skill.strip())
    if skills:
        job["skills"] = skills

    return job


async def fetch_jobs():
    logger.info("-" * 60)
    logger.info("Starting browser and navigating to Djinni base URL")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=DJINNI_HEADLESS)
        page = await browser.new_page()

        await page.route("**/*", block_resources)

        all_jobs = []

        page_num = 1
        while True:
            paginated_url = build_paginated_url(DJINNI_URL, page_num)
            logger.info(f"Fetching page {page_num}: {paginated_url}")
            await page.goto(paginated_url)

            # Wait for job listings
            await page.wait_for_selector("ul.list-unstyled > li", timeout=5000)
            job_items = await page.query_selector_all("ul.list-unstyled > li")

            if not job_items:
                logger.info("No job listings found. Stopping pagination.")
                break

            for i, item in enumerate(job_items, start=1):
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

            # Then check pagination links (AFTER scraping)
            pagination_items = await page.query_selector_all(
                "ul.pagination li.page-item a.page-link"
            )
            page_numbers = []

            for item in pagination_items:
                text = await item.text_content()
                if text and text.strip().isdigit():
                    page_numbers.append(int(text.strip()))

            logger.info(f"Pagination buttons found: {page_numbers}")

            # Stop if the next page number is not listed
            if (page_num + 1) not in page_numbers:
                logger.info(
                    f"No button for page {page_num + 1}. Stopping pagination."
                )
                break

            page_num += 1  # go to the next page

        await browser.close()
        logger.info(f"Browser closed. Total jobs fetched: {len(all_jobs)}")
        return all_jobs
