from typing import List, Dict, Any

from playwright.async_api import Page, Error as PlaywrightError

from logs.logger import logger
from src.config import JUST_JOIN_MAX_JOBS
from src.utils.fetching.anti_block import random_wait


async def scroll_and_fetch_jobs(page: Page) -> List[Dict[str, Any]]:
    """Scroll page and fetch job offers asynchronously."""
    from src.fetchers.justjoin.fetcher import parse_job_offer

    results = []
    seen_urls = set()
    job_counter = 1

    try:
        previous_height = await page.evaluate("document.body.scrollHeight")

        while True:
            await page.evaluate(
                "window.scrollBy(0, document.body.scrollHeight)"
            )
            await page.wait_for_timeout(60000)
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == previous_height:
                break
            previous_height = new_height

            offers = await page.query_selector_all("a.offer-card")
            all_jobs = []

            for offer in offers:
                # Jobs limit
                # Use total count to stop, not just current batch
                if len(results) + len(all_jobs) >= JUST_JOIN_MAX_JOBS:
                    logger.info(
                        f"Reached max job count of {JUST_JOIN_MAX_JOBS}, "
                        f"stopping scraping."
                    )
                    break

                job_data = await parse_job_offer(offer)
                if job_data["url"] and job_data["url"] not in seen_urls:
                    seen_urls.add(job_data["url"])
                    all_jobs.append(job_data)
                    logger.info(
                        f"{job_counter:>3}. {job_data['title']:<60} @ "
                        f"{job_data['company']}"
                    )
                    job_counter += 1

                    # Anti-block delay
                    await random_wait(0.5, 5.0)

            if not all_jobs:
                logger.info("No new offers loaded, stopping scroll.")
                break

            results.extend(all_jobs)

    except PlaywrightError as e:
        logger.error(f"Playwright error during scroll: {e}")

    return results
