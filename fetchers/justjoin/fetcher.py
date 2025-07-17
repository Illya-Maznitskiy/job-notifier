from playwright.async_api import async_playwright
from dotenv import load_dotenv

from utils.convert_bool import str_to_bool
from fetchers.justjoin.pagination import (
    scroll_and_fetch_jobs,
)
from logs.logger import logger
import os


load_dotenv()


JUST_JOIN_URL = os.getenv("JUST_JOIN_URL")
JUST_JOIN_HEADLESS = str_to_bool(os.getenv("JUST_JOIN_HEADLESS", "false"))


async def setup_page(playwright, url):
    """
    Launch browser, open page, handle cookies, and wait for offers.
    """
    logger.info("-" * 60)
    logger.info("Starting setup page")
    browser = await playwright.chromium.launch(headless=JUST_JOIN_HEADLESS)
    page = await browser.new_page()
    await page.goto(url)

    try:
        await page.click("#cookiescript_reject", timeout=5000)
        logger.info("Cookie consent rejected.")
    except Exception:
        logger.debug("No cookie popup found or already handled.")

    await page.wait_for_selector("a.offer-card", timeout=10000)
    return browser, page


async def parse_job_offer(offer):
    """
    Extract job details asynchronously from a job offer element.
    """
    title_el = await offer.query_selector("h3")
    title = await title_el.text_content() if title_el else None

    href = await offer.get_attribute("href")
    job_url = f"https://justjoin.it{href}" if href else None

    company_el = await offer.query_selector(
        "div.MuiBox-root.mui-1kb0cuq > span"
    )
    company = await company_el.text_content() if company_el else None

    salary_els = await offer.query_selector_all("div.mui-18ypp16 span")
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
                await currency_el.text_content() if currency_el else None
            )
        except ValueError:
            salary = None
            currency = None
    else:
        salary = None
        currency = None

    location_el = await offer.query_selector("span.mui-1o4wo1x")
    location = await location_el.text_content() if location_el else None

    skill_els = await offer.query_selector_all(
        "div.skill-tag-1 div.mui-jikuwi"
    )
    skills = [await s.text_content() for s in skill_els]

    return {
        "title": title.strip() if title else None,
        "url": job_url,
        "company": company.strip() if company else None,
        "salary": salary.strip() if salary else None,
        "currency": currency.strip() if currency else None,
        "location": location.strip() if location else None,
        "skills": [s.strip() for s in skills],
    }


async def fetch_jobs():
    """
    Launch browser and scrape job offers from target URL asynchronously.
    """
    url = JUST_JOIN_URL

    logger.info("-" * 60)
    logger.info(f"Starting fetch_jobs for URL: {url}")

    try:
        async with async_playwright() as p:
            browser, page = await setup_page(p, url)

            # Scroll and fetch incrementally
            results = await scroll_and_fetch_jobs(page)

            await browser.close()
            logger.info("Browser closed. Finished fetching jobs.")
            return results

    except Exception as e:
        logger.error(f"Error in fetch_jobs: {e}", exc_info=True)
        raise
