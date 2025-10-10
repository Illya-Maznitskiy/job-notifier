import re

from playwright.async_api import async_playwright, ViewportSize
from tqdm.asyncio import tqdm_asyncio

from logs.logger import logger
from src.config import NO_FLUFF_HEADLESS, NO_FLUFF_MAX_JOBS
from src.utils.fetching.anti_block import get_random_user_agent, random_wait
from src.utils.fetching.fetcher_optimization import block_resources


def clean_text(text: str) -> str:
    """Normalize spaces and remove non-breaking spaces."""
    try:
        return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()
    except Exception as err:
        logger.error(f"Failed to clean text: {err}")
        return ""


def clean_location(text: str) -> str:
    """Remove phone suffixes and clean text."""
    try:
        cleaned = re.sub(r"\+\d+$", "", text)
        return clean_text(cleaned)
    except Exception as err:
        logger.error(f"Failed to clean location: {err}")
        return ""


async def fetch_nofluff_jobs(url: str) -> list[dict]:
    """Fetch NoFluffJobs postings."""
    logger.info("Opening NoFluffJobs URL")
    all_jobs: list[dict] = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=NO_FLUFF_HEADLESS,
                args=["--disable-blink-features=AutomationControlled"],
            )

            # Random User-Agent
            ua = get_random_user_agent()
            logger.info(f"User-agent: {ua}")
            page = await browser.new_page(
                viewport=ViewportSize(width=1000, height=700)
            )
            await page.route("**/*", block_resources)
            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            logger.info("Page loaded successfully.")

            # Accept cookies if present
            try:
                consent_button = page.locator(
                    "button[data-action='consent'][data-action-type='accept']"
                )
                await consent_button.wait_for(state="visible", timeout=30_000)
                await consent_button.click()
                logger.info("Cookie consent accepted (Akceptuj wszystkie).")
            except Exception as cookie_err:
                logger.warning(f"No cookie consent to close: {cookie_err}")

            job_cards = page.locator("a.posting-list-item")

            while True:
                count_before = await job_cards.count()
                load_more_button = page.locator(
                    "button", has_text="Pokaż kolejne oferty"
                )

                # the fetcher at this moment works without that wait selector
                # try:
                #     await page.wait_for_selector(
                #         ".cdk-overlay-container",
                #         state="detached",
                #         timeout=15_000,
                #     )
                # except TimeoutError as overlay_err:
                #     pass
                #     # logger.debug(
                #     #     f"Overlay wait skipped or failed: {overlay_err}"
                #     # )

                if await load_more_button.count() == 0:
                    logger.info(
                        "'Pokaż kolejne oferty' "
                        "button not found — reached end."
                    )
                    break

                if await load_more_button.is_enabled():
                    await page.evaluate(
                        "window.scrollTo(0, document.body.scrollHeight)"
                    )
                    try:

                        await load_more_button.scroll_into_view_if_needed(
                            timeout=60_000
                        )
                        await page.evaluate(
                            """
                            Array.from(document.querySelectorAll('button'))
                                 .find(b => b.textContent.includes
                                 ('Pokaż kolejne oferty'))
                                 ?.click()
                            """
                        )
                        await page.wait_for_timeout(3000)
                        await page.wait_for_function(
                            f"document.querySelectorAll"
                            f"('a.posting-list-item').length > {count_before}",
                            timeout=60_000,
                        )
                        count_after = await job_cards.count()
                        logger.info(
                            f"Loaded {count_after - count_before} "
                            f"new jobs (total: {count_after})."
                        )

                        if (
                            count_after == count_before
                            or count_after >= NO_FLUFF_MAX_JOBS
                        ):
                            break
                    except Exception as err:
                        logger.warning(
                            f"Failed to scroll/click load-more button: {err}"
                        )
                        break

                else:
                    logger.warning("Failed to scroll/click load-more button")
                    break

            total_count = min(await job_cards.count(), NO_FLUFF_MAX_JOBS)
            logger.info(f"Total jobs loaded: {total_count}")

            for i in tqdm_asyncio(
                range(total_count), desc="Fetching jobs", mininterval=120.0
            ):
                job = job_cards.nth(i)
                try:
                    title = await job.locator(
                        "h3.posting-title__position"
                    ).text_content()
                    company = await job.locator(
                        "h4.company-name"
                    ).text_content()
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

                    job_data = {
                        "url": (
                            f"https://nofluffjobs.com{href}" if href else ""
                        ),
                        "title": clean_text(title) if title else "",
                        "company": clean_text(company) if company else "",
                        "skills": [clean_text(s) for s in skills],
                        "salary": clean_text(salary_raw) if salary_raw else "",
                        "location": (
                            clean_location(location_raw)
                            if location_raw
                            else ""
                        ),
                    }
                    all_jobs.append(job_data)
                    logger.debug(
                        f"{i+1:>3}. {job_data['title']:<60} @ "
                        f"{job_data['company']}"
                    )

                    # Anti-block delay
                    await random_wait(0.5, 5.0)
                except Exception as job_err:
                    logger.warning(f"Failed to parse job {i+1}: {job_err}")

            await browser.close()
    except Exception as fetch_err:
        logger.error(f"Failed to fetch jobs: {fetch_err}")

    logger.info(f"Finished scraping {len(all_jobs)} jobs.")
    return all_jobs
