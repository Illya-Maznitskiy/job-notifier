import os

import requests
from dotenv import load_dotenv

from logs.logger import logger
from src.config import (
    JOOBLE_MAX_JOBS,
    JOOBLE_KEYWORDS,
    JOOBLE_LOCATION,
    JOOBLE_RADIUS,
    JOOBLE_MIN_SALARY,
    JOOBLE_SEARCH_MODE,
    JOOBLE_DATE,
)

load_dotenv()
api_key = os.getenv("JOOBLE_API_KEY")


def sanitize_job(job):
    if not job.get("company"):
        job["company"] = "Unknown Company"
    return job


def fetch_jooble_jobs(max_jobs=JOOBLE_MAX_JOBS):
    logger.info("-" * 60)
    logger.info("Fetching jobs from Jooble...")

    if not api_key:
        logger.error(
            "No Jooble API key found in environment variable "
            "'JOOBLE_API_KEY'. Aborting fetch."
        )
        return []

    api_url = f"https://jooble.org/api/{api_key}"
    all_jobs = []
    page = 1
    max_pages = 1000  # Prevent infinite loops just in case

    while page <= max_pages:
        payload = {
            "keywords": JOOBLE_KEYWORDS,
            "location": JOOBLE_LOCATION,
            "page": page,
            "radius": JOOBLE_RADIUS,
            "salary": JOOBLE_MIN_SALARY,
            "searchMode": JOOBLE_SEARCH_MODE,
            "date": JOOBLE_DATE,
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
        for i, job in enumerate(jobs):
            if "link" in job:
                job["url"] = job.pop("link")
            jobs[i] = sanitize_job(job)  # update the list with sanitized job

        for i, job in enumerate(jobs, len(all_jobs) + 1):
            company = job.get("company") or "Unknown Company"
            title = job.get("title", "No Title")
            logger.info(f"{i:>3}. {title.strip():<60} @ {company.strip()}")

        all_jobs.extend(jobs)

        # Limit jobs
        if len(all_jobs) >= max_jobs:
            all_jobs = all_jobs[:max_jobs]  # trim extra
            logger.info(f"Maximum jobs limit reached: {max_jobs}")
            break

        page += 1

    logger.info("Total jobs fetched from Jooble: %d", len(all_jobs))

    return all_jobs
