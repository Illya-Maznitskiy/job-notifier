import os
import re

from dotenv import load_dotenv
from playwright.async_api import async_playwright

from logs.logger import logger
from utils.convert_bool import str_to_bool

load_dotenv()
NO_FLUFF_HEADLESS = str_to_bool(os.getenv("NO_FLUFF_HEADLESS", "false"))


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

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="pl-PL",
        )

        page = await context.new_page()

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
        jobs = []

        while True:
            count_before = await job_cards.count()

            load_more_button = page.locator(
                "button", has_text="Pokaż kolejne oferty"
            )

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
                await load_more_button.click()
                await page.wait_for_timeout(3000)

                # Wait for new jobs to load
                await page.wait_for_function(
                    f"document.querySelectorAll('a.posting-list-item').length > {count_before}",
                    timeout=30000,
                )

                count_after = await job_cards.count()
                logger.info(
                    f"Loaded {count_after - count_before} new jobs (total: {count_after})."
                )

                if count_after == count_before:
                    logger.info("No new jobs loaded — breaking.")
                    break
            else:
                logger.info(
                    "'Pokaż kolejne oferty' button disabled — reached end."
                )
                break

        # Now fetch all jobs after loading is done
        total_count = await job_cards.count()
        logger.info(f"Total jobs loaded: {total_count}")

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

            jobs.append(job_data)

            logger.info(
                f"{i + 1:>3}. {job_data['title']:<60} @ {job_data['company']}"
            )

        logger.info(f"Finished scraping {len(jobs)} jobs.")
        await browser.close()
        return jobs
