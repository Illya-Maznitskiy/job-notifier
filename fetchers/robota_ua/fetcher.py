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


async def auto_scroll(page, scroll_step=1050, max_scrolls: int = 5):
    # Give the page time to settle before starting scroll
    await asyncio.sleep(1)

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

    # 1) Try company name from alt or title attribute
    # of img inside company-logo div
    company_img = await item.query_selector("div.company-logo img")
    company = None
    if company_img:
        company = await company_img.get_attribute("alt")
        if not company:
            company = await company_img.get_attribute("title")
        if company:
            company = company.strip()

    # 2) If company not found, try getting company name from <span>
    if not company:
        # Query all spans with class containing santa-mr-20 (or exact match)
        span_el = await item.query_selector("span.santa-mr-20")
        if span_el:
            text = await span_el.text_content()
            if text:
                company = text.strip()

    if company:
        job["company"] = company

    # Salary info - first <span> inside div.santa-mb-10 with
    # text containing digits or ₴
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
    logger.info("Launching browser for robota.ua scraping")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=ROBOTA_UA_HEADLESS,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = await browser.new_page(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36",
        )

        all_jobs = []

        logger.info(f"Fetching robota.ua page: {ROBOTA_UA_URL}")
        await page.goto(ROBOTA_UA_URL)

        while True:
            # Scroll page fully so all jobs load
            await auto_scroll(page)
            await page.wait_for_selector("a.card", timeout=30000)

            job_items = await page.query_selector_all("a.card")
            if not job_items:
                logger.info("No job items found on the page.")
                break

            # Filter out jobs inside recommended section
            filtered_job_items = []
            for card in job_items:
                parent_alliance = await card.evaluate(
                    "(node) => node.closest"
                    "('alliance-recommended-vacancy-list')"
                )
                if not parent_alliance:
                    filtered_job_items.append(card)

            # Extract job details from filtered cards
            for i, item in enumerate(filtered_job_items, start=1):
                job = await extract_robota_ua_job(item)

                if not job or "title" not in job or "url" not in job:
                    logger.warning("Skipped job due to missing title or URL")
                    continue

                # Check if it's remote
                tag_elements = await item.query_selector_all("div, span")
                is_remote = False

                for tag_el in tag_elements:
                    tag_text = (await tag_el.inner_text()).strip().lower()
                    if (
                        "віддалена" in tag_text
                        or "віддалена робота" in tag_text
                    ):
                        is_remote = True
                        break

                if not is_remote:
                    logger.info(
                        f"Skipped job #{job.get('company', 'unknown')} "
                        f"{job.get('title', 'unknown')} — not remote"
                    )
                    continue  # this prevents adding the job to the list

                # If remote, keep and log
                all_jobs.append(job)
                logger.info(
                    f"{len(all_jobs):>3}. {job['title']:<60} @ {job.get('company', 'unknown')}"
                )

            # Go to next page or break if no next page
            has_next = await click_next_page(page)
            if not has_next:
                logger.info("No more pages to fetch.")
                break

        await browser.close()
        logger.info(f"Scraping done. Total jobs fetched: {len(all_jobs)}")
        return all_jobs
