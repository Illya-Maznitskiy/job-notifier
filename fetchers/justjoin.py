import asyncio
import json
import logging
from pathlib import Path

from playwright.async_api import async_playwright

from logs.logger import logger


async def fetch_jobs():
    """
    Fetches junior Python developer jobs from justjoin.it asynchronously.
    """
    url = "https://justjoin.it/job-offers/remote?keyword=junior+python+developer&orderBy=DESC&sortBy=published"

    logger.info("-" * 60)
    logger.info(f"Starting fetch_jobs for URL: {url}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto(url)

            try:
                await page.click("#cookiescript_reject", timeout=5000)
                logger.info("Cookie consent rejected.")
            except Exception:
                logger.debug("No cookie popup found or already handled.")

            await page.wait_for_selector("a.offer-card", timeout=10000)
            offers = await page.query_selector_all("a.offer-card")

            results = []

            for i, offer in enumerate(offers, 1):
                # Title
                title_el = await offer.query_selector("h3")
                title = await title_el.text_content() if title_el else None

                # Job URL
                href = await offer.get_attribute("href")
                job_url = f"https://justjoin.it{href}" if href else None

                # Company
                company_el = await offer.query_selector(
                    "div.MuiBox-root.mui-1kb0cuq > span"
                )
                company = (
                    await company_el.text_content() if company_el else None
                )

                # Salary
                salary_els = await offer.query_selector_all(
                    "div.mui-18ypp16 span"
                )
                if len(salary_els) >= 2:
                    min_salary_text = await salary_els[0].text_content()
                    max_salary_text = await salary_els[1].text_content()
                    currency_el = await offer.query_selector(
                        "div.mui-18ypp16 span.mui-1m61siv"
                    )

                    try:
                        min_salary = int(min_salary_text.replace(" ", ""))
                        max_salary = int(max_salary_text.replace(" ", ""))
                        average_salary = (min_salary + max_salary) // 2
                        salary = f"{average_salary}"
                        currency = (
                            await currency_el.text_content()
                            if currency_el
                            else None
                        )
                    except ValueError:
                        salary = None
                        currency = None
                else:
                    salary = None
                    currency = None

                # Location
                location_el = await offer.query_selector("span.mui-1o4wo1x")
                location = (
                    await location_el.text_content() if location_el else None
                )

                # Skills
                skill_els = await offer.query_selector_all(
                    "div.skill-tag-1 div.mui-jikuwi"
                )
                skills = [await s.text_content() for s in skill_els]

                job_data = {
                    "title": title.strip() if title else None,
                    "url": job_url,
                    "company": company.strip() if company else None,
                    "salary": salary.strip() if salary else None,
                    "currency": currency.strip() if currency else None,
                    "location": location.strip() if location else None,
                    "skills": [s.strip() for s in skills],
                }

                logger.info(
                    f"{i:>2}. {job_data['title']:<50} @ {job_data['company']}"
                )

                results.append(job_data)

            await browser.close()
            logger.info("Browser closed. Finished fetching jobs.")
            return results

    except Exception as e:
        logger.error(f"Error in fetch_jobs: {e}", exc_info=True)
        raise


def save_jobs_to_json(jobs, filename="justjoin_jobs.json"):
    """
    Saves job list to JSON file in the storage directory.
    """
    # Get the root directory (the one containing your main script or .git, etc.)
    root_dir = Path(__file__).resolve().parent.parent
    storage_dir = root_dir / "storage"
    storage_dir.mkdir(exist_ok=True)

    filepath = storage_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    logger.info("-" * 60)
    logger.info(f"Saved {len(jobs)} jobs to {filepath}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    jobs = asyncio.run(fetch_jobs())

    if not jobs:
        logger.info("no_jobs")
    else:
        save_jobs_to_json(jobs)
