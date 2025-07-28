import os

import requests
from dotenv import load_dotenv

from logs.logger import logger

load_dotenv()
api_key = os.getenv("JOOBLE_API_KEY")


def fetch_jooble_jobs():
    logger.info("-" * 60)
    logger.info("Fetching jobs from Jooble...")

    if not api_key:
        logger.error(
            "No Jooble API key found in environment variable 'JOOBLE_API_KEY'. Aborting fetch."
        )
        return []

    api_url = f"https://jooble.org/api/{api_key}"
    all_jobs = []
    page = 1
    max_pages = 10  # Prevent infinite loops just in case

    while page <= max_pages:
        payload = {
            "keywords": "python remote",  # stricter search, no OR
            "location": "Poland",
            "page": page,
            "radius": "1000",
            "salary": 0,
        }
        logger.debug("Requesting page %d", page)
        logger.debug("Request payload: %s", payload)

        response = requests.post(api_url, json=payload)
        logger.debug("Response status code: %d", response.status_code)

        if response.status_code != 200:
            logger.error(
                "Jooble API error: %s %s", response.status_code, response.text
            )
            break

        data = response.json()
        jobs = data.get("jobs", [])
        logger.info("Fetched %d jobs from page %d", len(jobs), page)

        if not jobs:
            break  # No more jobs on next page

        # Rename 'link' key to 'URL' in each job dict
        for job in jobs:
            if "link" in job:
                job["URL"] = job.pop("link")

        for i, job in enumerate(jobs, len(all_jobs) + 1):
            company = job.get("company", "Unknown Company")
            title = job.get("title", "No Title")
            url = job.get("URL", "No URL")
            logger.info(
                "%d. %s - %s (%s)", i, company.strip(), title.strip(), url
            )

        all_jobs.extend(jobs)
        page += 1

    logger.info("Total jobs fetched from Jooble: %d", len(all_jobs))
    return all_jobs
