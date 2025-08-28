import re

from playwright.async_api import async_playwright

from logs.logger import logger
from src.config import NO_FLUFF_HEADLESS, NO_FLUFF_MAX_JOBS
from src.utils.fetching.anti_block import get_random_user_agent
from src.utils.fetching.fetcher_optimization import block_resources


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def clean_location(text: str) -> str:
    # Remove "+7" or similar suffixes and clean
    cleaned = re.sub(r"\+[\d]+$", "", text)
    return clean_text(cleaned)


async def fetch_nofluff_jobs(url: str) -> list[dict]:
    """
    Fetches full job data from NoFluffJobs.
    """
    logger.info(f"Opening NoFluffJobs URL")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=NO_FLUFF_HEADLESS,
            args=["--disable-blink-features=AutomationControlled"],
        )

        # Random User-Agent
        ua = get_random_user_agent()
        logger.info(f"User-agent: {ua}")
        page = await browser.new_page(user_agent=ua)

        await page.route("**/*", block_resources)

        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        logger.info("Page loaded successfully.")

        # Accept cookies if present
        try:
            consent_button = page.locator(
                "button[data-action='consent'][data-action-type='accept']"
            )

            # Wait up to 30 seconds for the cookie banner to appear
            await consent_button.wait_for(state="visible", timeout=30_000)
            await consent_button.click()
            logger.info("Cookie consent accepted (Akceptuj wszystkie).")

        except Exception as e:
            logger.warning(
                f"No cookie consent to close or timeout occurred: {e}"
            )

        job_cards = page.locator("a.posting-list-item")
        all_jobs = []

        while True:
            # Jobs limit
            if len(all_jobs) >= NO_FLUFF_MAX_JOBS:
                logger.info(
                    f"Reached max job count of {NO_FLUFF_MAX_JOBS}, stopping scraping."
                )
                break

            count_before = await job_cards.count()

            load_more_button = page.locator(
                "button", has_text="Pokaż kolejne oferty"
            )
            # Wait for any overlay blocking pointer events to disappear
            try:
                await page.wait_for_selector(
                    ".cdk-overlay-container", state="detached", timeout=15000
                )
            except Exception:
                pass

            if await load_more_button.count() == 0:
                logger.info(
                    "'Pokaż kolejne oferty' button not found — reached end of job list."
                )
                break

            # Make sure it's visible/enabled before clicking
            if await load_more_button.is_enabled():
                await page.evaluate(
                    "window.scrollTo(0, document.body.scrollHeight)"
                )
                logger.info(
                    "Scrolled to bottom before clicking 'Pokaż kolejne oferty' button"
                )
                await load_more_button.scroll_into_view_if_needed()
                logger.info("Clicking 'Pokaż kolejne oferty' button...")
                await page.evaluate(
                    """
                    Array.from(document.querySelectorAll('button'))
                         .find(b => b.textContent.includes('Pokaż kolejne oferty'))
                         ?.click()
                """
                )
                await page.wait_for_timeout(3000)

                # Wait for new all_jobs to load
                await page.wait_for_function(
                    f"document.querySelectorAll('a.posting-list-item').length > {count_before}",
                    timeout=30000,
                )

                count_after = await job_cards.count()
                logger.info(
                    f"Loaded {count_after - count_before} new all_jobs (total: {count_after})."
                )

                if count_after == count_before:
                    logger.info("No new all_jobs loaded — breaking.")
                    break
            else:
                logger.info(
                    "'Pokaż kolejne oferty' button disabled — reached end."
                )
                break

        # Now fetch all all_jobs after loading is done
        total_count = await job_cards.count()
        logger.info(f"Total all_jobs loaded: {total_count}")

        for i in range(total_count):
            job = job_cards.nth(i)

            title = await job.locator(
                "h3.posting-title__position"
            ).text_content()
            company = await job.locator("h4.company-name").text_content()
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
                "url": f"https://nofluffjobs.com{href}" if href else "",
                "title": clean_text(title) if title else "",
                "company": clean_text(company) if company else "",
                "skills": [clean_text(s) for s in skills],
                "salary": clean_text(salary_raw) if salary_raw else "",
                "location": (
                    clean_location(location_raw) if location_raw else ""
                ),
            }

            all_jobs.append(job_data)

            logger.info(
                f"{i + 1:>3}. {job_data['title']:<60} @ {job_data['company']}"
            )

        logger.info(f"Finished scraping {len(all_jobs)} all_jobs.")
        await browser.close()
        return all_jobs
