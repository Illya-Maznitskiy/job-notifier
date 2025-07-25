import asyncio
import os

from dotenv import load_dotenv
from playwright.async_api import async_playwright

from fetchers.robota_ua.pagination import click_next_page
from logs.logger import logger
from utils.convert_bool import str_to_bool

load_dotenv()

ROBOTA_UA_URL = os.getenv("ROBOTA_UA_URL", "https://robota.ua/ua/jobs")
ROBOTA_UA_HEADLESS = str_to_bool(os.getenv("ROBOTA_UA_HEADLESS", "true"))
BASE_URL = "https://robota.ua"


async def auto_scroll(page, scroll_step=900, max_scrolls: int = 7):
    previous_scroll = None
    scroll_count = 0

    while True:
        if max_scrolls is not None and scroll_count >= max_scrolls:
            break

        current_scroll = await page.evaluate("window.pageYOffset")
        max_scroll = await page.evaluate(
            "document.body.scrollHeight - window.innerHeight"
        )

        if previous_scroll == current_scroll or current_scroll >= max_scroll:
            break

        previous_scroll = current_scroll
        next_scroll = min(current_scroll + scroll_step, max_scroll)
        await page.evaluate(f"window.scrollTo(0, {next_scroll})")
        await asyncio.sleep(1)  # wait for content to load

        scroll_count += 1


async def extract_robota_ua_job(item) -> dict:
    job = {}

    # Job URL (relative -> absolute)
    url = await item.get_attribute("href")
    if url:
        job["url"] = BASE_URL + url.strip()

    # Job title
    title_el = await item.query_selector("h2.santa-typo-h3")
    if title_el:
        title = await title_el.text_content()
        if title:
            job["title"] = title.strip()

    # Company name from alt/title attribute of img inside company-logo div
    company_img = await item.query_selector("div.company-logo img")
    if company_img:
        company = await company_img.get_attribute("alt")
        if company:
            job["company"] = company.strip()

    # Salary info - first <span> inside div.santa-mb-10 with text containing digits or ₴
    salary_el = await item.query_selector("div.santa-mb-10 > span")
    if salary_el:
        salary = await salary_el.text_content()
        if salary and any(ch.isdigit() for ch in salary):
            job["salary"] = salary.strip()

    # Location (with possible remote note)
    location_el = await item.query_selector(
        "div.santa-flex.santa-items-center > span"
    )
    if location_el:
        location = await location_el.text_content()
        if location:
            job["location"] = location.strip()

    return job


async def fetch_robota_ua_jobs():
    logger.info("-" * 60)
    logger.info(f"Launching browser for robota.ua scraping")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=ROBOTA_UA_HEADLESS)
        page = await browser.new_page()
        all_jobs = []

        logger.info(f"Fetching robota.ua page: {ROBOTA_UA_URL}")
        await page.goto(ROBOTA_UA_URL)

        while True:
            # Scroll page fully so all jobs load
            await auto_scroll(page)
            await page.wait_for_selector("a.card", timeout=10000)

            job_items = await page.query_selector_all("a.card")
            if not job_items:
                logger.info("No job items found on the page.")
                break

            # Filter out jobs inside recommended section
            filtered_job_items = []
            for card in job_items:
                parent_alliance = await card.evaluate(
                    "(node) => node.closest('alliance-recommended-vacancy-list')"
                )
                if not parent_alliance:
                    filtered_job_items.append(card)

            # Extract job details from filtered cards
            for i, item in enumerate(filtered_job_items, start=1):
                job = await extract_robota_ua_job(item)
                if "title" in job and "url" in job:
                    all_jobs.append(job)
                    logger.info(
                        f"{len(all_jobs):>2}. {job['title']} @ "
                        f"{job.get('company', 'unknown')} "
                        f"({job.get('location', 'unknown')})"
                    )
                else:
                    logger.warning(
                        f"Skipped job #{i} due to missing title or URL"
                    )

            # Go to next page or break if no next page
            has_next = await click_next_page(page)
            if not has_next:
                logger.info("No more pages to fetch.")
                break

        await browser.close()
        logger.info(f"Scraping done. Total jobs fetched: {len(all_jobs)}")
        return all_jobs
