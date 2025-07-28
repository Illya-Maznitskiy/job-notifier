from playwright.async_api import async_playwright
from fetchers.models.djinni.pagination import build_paginated_url
from logs.logger import logger






async def extract_job_data(item) -> dict:

async def fetch_jobs(max_pages: int = 5):
    logger.info("-" * 60)
    logger.info("Starting browser and navigating to Djinni base URL")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=DJINNI_HEADLESS)
        page = await browser.new_page()
        all_jobs = []

        for page_num in range(1, max_pages + 1):
            paginated_url = build_paginated_url(DJINNI_URL, page_num)
            logger.info(f"Fetching page {page_num}: {paginated_url}")
            await page.goto(paginated_url)

            # Wait for job listings
            await page.wait_for_selector("ul.list-unstyled > li", timeout=5000)
            job_items = await page.query_selector_all("ul.list-unstyled > li")

            if not job_items:
                logger.info("No job listings found. Stopping pagination.")
                break

            for i, item in enumerate(job_items, start=1):
                job = await extract_job_data(item)
                if "title" in job and "url" in job:
                    all_jobs.append(job)
                    logger.info(
                        f"{len(all_jobs):>2}. {job['title']} @ "
                        f"{job.get('company', 'unknown')} "
                        f"({job.get('location', 'unknown')})"
                    )
                else:
                    logger.warning(
                        f"Skipped job #{i} due to missing title or url"
                    )

            # Then check pagination links (AFTER scraping)
            pagination_items = await page.query_selector_all(
                "ul.pagination li.page-item a.page-link"
            )
            page_numbers = []

            for item in pagination_items:
                text = await item.text_content()
                if text and text.strip().isdigit():
                    page_numbers.append(int(text.strip()))

            logger.info(f"Pagination buttons found: {page_numbers}")

            # Stop if the next page number is not listed
            if (page_num + 1) not in page_numbers:
                logger.info(
                    f"No button for page {page_num + 1}. Stopping pagination."
                )
                break

        await browser.close()
        logger.info(f"Browser closed. Total jobs fetched: {len(all_jobs)}")
        return all_jobs
