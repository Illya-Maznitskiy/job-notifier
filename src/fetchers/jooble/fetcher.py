import os
from typing import Dict, Any, List
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


def ensure_company_name(job: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure job has a company name."""
    if not job.get("company"):
        job["company"] = "Unknown Company"
    return job


def fetch_jooble_jobs(max_jobs: int = JOOBLE_MAX_JOBS) -> List[Dict[str, Any]]:
    """Fetch jobs from Jooble API."""
    logger.info("-" * 60)
    logger.info("Fetching jobs from Jooble...")

    if not api_key:
        logger.error(
            "No Jooble API key found in environment variable 'JOOBLE_API_KEY'."
        )
        return []

    api_url = f"https://jooble.org/api/{api_key}"
    all_jobs: List[Dict[str, Any]] = []
    page = 1
    max_pages = 1000  # Prevent infinite loops, because infinity is scary

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
        logger.debug(f"Requesting page {page}")
        logger.debug(f"Request payload: {payload}")

        try:
            response: requests.Response = requests.post(api_url, json=payload)
            response.raise_for_status()
            jobs: List[Dict[str, Any]] = response.json().get("jobs", [])
        except Exception as req_err:
            logger.error(f"Jooble API request failed: {req_err}")
            jobs = []

        logger.info(f"Fetched {len(jobs)} jobs from page {page}")

        if not jobs:
            break

        # Rename 'link' key to 'URL' in each job dict
        for i, job in enumerate(jobs):
            if "link" in job:
                job["url"] = job.pop("link")
            jobs[i] = ensure_company_name(job)

        for i, job in enumerate(jobs, len(all_jobs) + 1):
            company = job.get("company") or "Unknown Company"
            title = job.get("title", "No Title")
            logger.debug(f"{i:>3}. {title.strip():<60} @ {company.strip()}")

        all_jobs.extend(jobs)

        if len(all_jobs) >= max_jobs:
            all_jobs = all_jobs[:max_jobs]
            logger.info(f"Maximum jobs limit reached: {max_jobs}")
            break

        page += 1

    logger.info(f"Total jobs fetched from Jooble: {len(all_jobs)}")

    return all_jobs
