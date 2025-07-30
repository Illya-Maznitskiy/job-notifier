import asyncio
import os
import re
from asyncio import gather
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from dotenv import load_dotenv
from playwright.async_api import async_playwright

from logs.logger import logger
from utils.convert_bool import str_to_bool


load_dotenv()
PRACUJ_HEADLESS = str_to_bool(os.getenv("PRACUJ_HEADLESS", "false"))


async def accept_cookies_if_present(page):
    logger.info("-" * 60)
    await asyncio.sleep(1)

    # Try clicking the first cookie button
    try:
        await page.locator("button[data-test='button-submitCookie']").click(
            timeout=3000
        )
        logger.info("Accepted cookies using data-test locator")
    except Exception:
        logger.info("First cookie button not found")

    # Try clicking the second cookie button
    try:
        await page.get_by_role("button", name="OK, rozumiem").click(
            timeout=3000
        )
        logger.info(
            "Accepted cookies using fallback locator for 'OK, rozumiem'"
        )
    except Exception:
        logger.debug("Second cookie button not found, continuing")


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


async def safe_text(locator, field_name=""):
    try:
        return await locator.text_content(timeout=2000) or ""
    except Exception as e:
        if "offer-salary" in field_name:
            logger.debug("No salary info")
        else:
            logger.debug(f"Failed to get text content: {e}")
        return ""


async def safe_attr(locator, attr):
    try:
        return await locator.get_attribute(attr, timeout=5000) or ""
    except Exception as e:
        logger.debug(f"Failed to get attribute '{attr}': {e}")
        return ""


def remove_search_id_param(url: str) -> str:
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params.pop("searchId", None)  # Remove 'searchId' if present
    cleaned_query = urlencode(query_params, doseq=True)
    cleaned_url = parsed_url._replace(query=cleaned_query)
    return urlunparse(cleaned_url)


async def fetch_pracuj_jobs(url: str) -> list[dict]:
    logger.info("-" * 60)
    logger.info(f"Starting job fetch from: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=PRACUJ_HEADLESS)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(3000)
        await accept_cookies_if_present(page)

        jobs = []
        page_number = 1

        while True:
            logger.info(f"Fetching page {page_number}")
            try:
                await page.wait_for_selector(
                    "h2[data-test='offer-title']", timeout=10000
                )
            except Exception:
                logger.warning(
                    f"No job listings found on page {page_number}, stopping."
                )
                break

            cards = page.locator(
                "div[data-test='positioned-offer'], "
                "div[data-test='default-offer']"
            ).filter(
                has_not=page.locator("div[data-test='section-ad-container']")
            )

            count = await cards.count()
            logger.info(f"Found {count} job cards on page {page_number}")

            async def extract_job_data(i: int):
                logger.debug(f"Processing job {i + 1}/{count}")
                job = cards.nth(i)

                await job.scroll_into_view_if_needed()
                await page.wait_for_timeout(300)  # Give time for lazy content

                title = await safe_text(
                    job.locator("h2[data-test='offer-title']")
                )
                salary = await safe_text(
                    job.locator("span[data-test='offer-salary']"),
                    "offer-salary",
                )
                company = await safe_text(
                    job.locator("h3[data-test='text-company-name']")
                )
                city = await safe_text(
                    job.locator("h4[data-test='text-region']")
                )
                work_fmt = await safe_text(
                    job.locator("ul.tiles_bfrsaoj li").first
                )

                link = ""

                # First attempt: known data-test attributes
                link_locator = job.locator(
                    "a[data-test='link-offer-title'], "
                    "a[data-test='link-offer']"
                ).first
                try:
                    link = await link_locator.get_attribute(
                        "href", timeout=2000
                    )
                except Exception as e:
                    logger.debug(f"Preferred link not found: {e}")

                # Fallback: try all anchors within the job card
                if not link:
                    logger.debug("Trying fallback link search...")
                    try:
                        anchors = job.locator("a")
                        count_anchors = await anchors.count()
                        for j in range(count_anchors):
                            a = anchors.nth(j)
                            href = await safe_attr(a, "href")
                            if href and "/oferta/" in href:
                                link = href
                                logger.debug("Used fallback offer link.")
                                break
                    except Exception as e:
                        logger.debug(f"Fallback search failed: {e}")

                if not link:
                    logger.warning(f"No valid job link found for job {i + 1}")
                else:
                    link = remove_search_id_param(link)

                return {
                    "url": link,
                    "title": clean_text(title),
                    "company": clean_text(company),
                    "salary": clean_text(salary),
                    "city": clean_text(city),
                    "work_format": clean_text(work_fmt),
                }

            job_data_batch = await gather(
                *(extract_job_data(i) for i in range(count))
            )
            jobs.extend(job_data_batch)

            # Pagination
            next_button = page.locator(
                "button[data-test='bottom-pagination-button-next']"
            )
            try:
                if await next_button.is_enabled(timeout=2000):
                    logger.info(
                        "Next page button is enabled, continuing pagination."
                    )
                    await next_button.click()
                    await page.wait_for_timeout(3000)
                    await page.wait_for_selector(
                        "div[data-test='positioned-offer'], "
                        "div[data-test='default-offer']",
                        timeout=10000,
                    )
                    await page.mouse.wheel(0, 500)
                    await page.wait_for_timeout(300)
                    page_number += 1
                else:
                    logger.info(
                        "Next page button is disabled or not found, "
                        "ending pagination."
                    )
                    break
            except Exception:
                logger.info(
                    "Next page button not found or not clickable, "
                    "ending pagination."
                )
                break

        await browser.close()

    logger.info(f"Finished fetching jobs, total collected: {len(jobs)}")
    return jobs
