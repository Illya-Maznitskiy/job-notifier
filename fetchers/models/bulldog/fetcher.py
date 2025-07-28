import os

from dotenv import load_dotenv

from utils.convert_bool import str_to_bool
from logs.logger import logger

load_dotenv()

BULLDOG_URL = os.getenv("BULLDOG_URL", "https://bulldogjob.com/companies/jobs")
BULLDOG_HEADLESS = str_to_bool(os.getenv("BULLDOG_HEADLESS", "true"))





async def fetch_bulldog_jobs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=BULLDOG_HEADLESS)
        page = await browser.new_page()
        all_jobs = []

        logger.info(f"Fetching Bulldog page: {BULLDOG_URL}")
        await page.goto(BULLDOG_URL)

        await page.wait_for_selector("a.JobListItem_item__fYh8y", timeout=5000)
        job_items = await page.query_selector_all("a.JobListItem_item__fYh8y")

        if not job_items:
            logger.info("No job items found on the page.")
        else:
            for i, item in enumerate(job_items, start=1):
                job = await extract_bulldog_job(item)
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

        await browser.close()
        logger.info(f"Scraping done. Total jobs fetched: {len(all_jobs)}")
        return all_jobs
