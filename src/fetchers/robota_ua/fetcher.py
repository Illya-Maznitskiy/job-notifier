import asyncio
from typing import List

from playwright.async_api import async_playwright, ElementHandle, ViewportSize
from tqdm.asyncio import tqdm_asyncio

from src.config import ROBOTA_UA_URL, ROBOTA_UA_HEADLESS, ROBOTA_UA_MAX_JOBS
from src.fetchers.robota_ua.pagination import click_next_page
from logs.logger import logger
from src.utils.fetching.anti_block import get_random_user_agent, random_wait
from src.utils.fetching.fetcher_optimization import block_resources


async def auto_scroll(
    page, scroll_step: int = 1050, max_scrolls: int = 12
) -> None:
    """Auto-scroll page to load content."""
    await asyncio.sleep(1)  # give page time to settle

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


async def extract_robota_ua_job(item: ElementHandle) -> dict:
    """Extracts job details from an element handle."""
    job = {}

    # Job URL
    url = await item.get_attribute("href")
    if url:
        job["url"] = ROBOTA_UA_URL + url.strip()

    # Job title
    title_el = await item.query_selector("h2.santa-typo-h3")
    if title_el:
        title = await title_el.text_content()
        if title:
            job["title"] = title.strip()

    # Company name
    company_img = await item.query_selector("div.company-logo img")
    company = None
    if company_img:
        company = await company_img.get_attribute(
            "alt"
        ) or await company_img.get_attribute("title")
    if not company:
        span_el = await item.query_selector("span.santa-mr-20")
        if span_el:
            company = await span_el.text_content()

    if company:
        job["company"] = company.strip()

    # Salary info
    salary_el = await item.query_selector("div.santa-mb-10 > span")
    if salary_el:
        salary = await salary_el.text_content()
        if salary and any(char.isdigit() or char == "₴" for char in salary):
            job["salary"] = salary.strip()

    # Location
    location_el = await item.query_selector(
        "div.santa-flex.santa-items-center > span"
    )
    if location_el:
        location = await location_el.text_content()
        if location:
            job["location"] = location.strip()

    return job


async def fetch_robota_ua_jobs() -> List[dict]:
    """Fetches remote jobs from robota.ua."""
    logger.info("-" * 60)
    logger.info("Launching browser for robota.ua scraping")
    all_jobs: List[dict] = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=ROBOTA_UA_HEADLESS,
                args=["--disable-blink-features=AutomationControlled"],
            )

            # Random User-Agent
            ua = get_random_user_agent()
            page = await browser.new_page(
                viewport=ViewportSize(width=600, height=400)
            )
            await page.route("**/*", block_resources)
            logger.info(f"User-agent: {ua}")
            logger.info(f"Fetching robota.ua page: {ROBOTA_UA_URL}")
            await page.goto(ROBOTA_UA_URL, timeout=60000)

            while len(all_jobs) < ROBOTA_UA_MAX_JOBS:

                # debugging part ↓↓↓
                await asyncio.sleep(3)
                html_content = await page.content()
                logger.info(
                    f"Fetching robota.ua page HTML:\n{html_content[:1000]}"
                )
                # debugging part ↑↑↑

                await auto_scroll(page)
                await page.wait_for_selector("a.card", timeout=60000)

                job_items = await page.query_selector_all("a.card")
                if not job_items:
                    logger.info("No job items found on the page.")
                    break

                for item in tqdm_asyncio(
                    job_items, desc="Fetching jobs", mininterval=120.0
                ):
                    # Filter out jobs from 'recommended' section
                    is_recommended = await item.evaluate(
                        "node => node.closest("
                        "'alliance-recommended-vacancy-list')"
                    )
                    if is_recommended:
                        continue

                    job = await extract_robota_ua_job(item)
                    if not job.get("title") or not job.get("url"):
                        logger.warning(
                            "Skipped job due to missing title or URL"
                        )
                        continue

                    # Check for remote work tag
                    tags = [
                        (await tag.inner_text()).strip().lower()
                        for tag in await item.query_selector_all("div, span")
                    ]
                    is_remote = any("віддалена" in tag for tag in tags)

                    if not is_remote:
                        logger.info(
                            f"Skipped job #{job.get('company', 'unknown')} "
                            f"{job.get('title', 'unknown')} — not remote"
                        )
                        continue

                    all_jobs.append(job)
                    logger.debug(
                        f"{len(all_jobs):>3}. {job['title']:<60} @ "
                        f"{job.get('company', 'unknown')}"
                    )

                    # Anti-block delay
                    await random_wait(0.5, 5.0)

                # Job limit
                if len(all_jobs) >= ROBOTA_UA_MAX_JOBS:
                    logger.info(
                        f"Reached max job count of {ROBOTA_UA_MAX_JOBS}, "
                        f"stopping scraping."
                    )
                    break

                if not await click_next_page(page):
                    logger.info("No more pages to fetch.")
                    break

            await browser.close()
    except Exception as e:
        logger.error(f"An error occurred during scraping: {e}")
    finally:
        if browser:
            await browser.close()

    logger.info(f"Scraping done. Total jobs fetched: {len(all_jobs)}")
    return all_jobs
