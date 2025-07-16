from playwright.async_api import async_playwright
from logs.logger import logger

DJINNI_URL = "https://djinni.co/jobs/?primary_keyword=Python&salary=1000&exp_level=no_exp&exp_level=1y&exp_level=2y&employment=remote&region=eu"


async def extract_job_data(item) -> dict:
    job = {}

    title_el = await item.query_selector("h2 a.job-item__title-link")
    if title_el:
        title = await title_el.text_content()
        href = await title_el.get_attribute("href")
        if title:
            job["title"] = title.strip()
        if href:
            job["url"] = f"https://djinni.co{href}"

    company_el = await item.query_selector("a.text-body.js-analytics-event")
    if company_el:
        company = await company_el.text_content()
        if company:
            job["company"] = company.strip()

    location_el = await item.query_selector("span.location-text")
    if location_el:
        location = await location_el.text_content()
        if location:
            job["location"] = location.strip()

    salary_el = await item.query_selector(".job-item__salary")
    if salary_el:
        salary_text = (await salary_el.text_content()) or ""
        salary_text = salary_text.strip()
        if salary_text:
            parts = salary_text.split()
            if parts:
                job["salary"] = parts[0]
                if len(parts) > 1:
                    job["currency"] = " ".join(parts[1:])

    skills_elements = await item.query_selector_all(".job-item__tags span")
    skills = []
    for skill_el in skills_elements:
        skill = await skill_el.text_content()
        if skill:
            skills.append(skill.strip())
    if skills:
        job["skills"] = skills

    return job


async def fetch_jobs():
    logger.info("-" * 60)
    logger.info("Starting browser and navigating to Djinni...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(DJINNI_URL)

        logger.info("Waiting for job listings to load...")
        await page.wait_for_selector("ul.list-unstyled > li")

        job_items = await page.query_selector_all("ul.list-unstyled > li")
        jobs = []

        for i, item in enumerate(job_items, start=1):
            job = await extract_job_data(item)
            if "title" in job and "url" in job:
                jobs.append(job)
                logger.info(
                    f"{i:>2}. {job['title']} @ {job.get('company', 'unknown')} ({job.get('location', 'unknown')})"
                )
            else:
                logger.warning(f"Skipped job #{i} due to missing title or url")

        await browser.close()
        logger.info(f"Browser closed. Total jobs fetched: {len(jobs)}")
        return jobs
