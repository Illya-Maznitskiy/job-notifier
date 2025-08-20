import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy import select

from db.db import AsyncSessionLocal
from db.models import UserKeyword
from logs.logger import logger


load_dotenv()


# Get SCORE_THRESHOLD as an integer, default to 0 if not set
SCORE_THRESHOLD = int(os.getenv("SCORE_THRESHOLD", 0))


async def get_user_keywords(session, user_id: int) -> dict[str, int]:
    """Fetch all keywords for a user as {keyword: weight}."""
    result = await session.execute(
        select(UserKeyword).where(UserKeyword.user_id == user_id)
    )
    keywords = result.scalars().all()
    return {kw.keyword.lower(): kw.weight for kw in keywords}


def score_job(job: dict, keyword_weights: dict, user_id=None) -> int:
    """Score job based on keyword relevance."""
    logger.info("-" * 60)

    title = job.get("title", "")
    skills = job.get("skills", "")
    description = job.get("description", "")

    if isinstance(skills, list):
        skills = " ".join(skills)

    combined_text = " ".join([title, skills, description]).lower()

    score = 0
    for keyword, weight in keyword_weights.items():
        if keyword in combined_text:  # partial match
            score += weight

    logger.debug(
        f"Job '{job.get('title')}' scored {score} for user_id={user_id}"
    )

    return score


async def filter_jobs_for_user(
    session, user_id: int, jobs: list[dict]
) -> list[dict]:
    """Filter jobs for a single user based on their keywords."""
    logger.info("-" * 60)
    logger.info(f"Fetching keywords for user_id={user_id}")

    keyword_weights = await get_user_keywords(session, user_id)
    filtered_jobs = []

    for job in jobs:
        score = score_job(job, keyword_weights, user_id)
        if score >= SCORE_THRESHOLD:
            filtered_jobs.append({**job, "score": score})

    filtered_jobs.sort(key=lambda job: job["score"], reverse=True)
    return filtered_jobs


async def main():
    async with AsyncSessionLocal() as session:
        # Mock a job
        jobs = [
            {
                "title": "Python Developer",
                "company": "ABC",
                "skills": ["python"],
                "url": "http://...",
                "description": "Looking for an experienced Python developer.",
            }
        ]

        # Mock user keywords instead of fetching from DB
        user_id = 1
        keyword_weights = {"python": 10}  # pretend the user has this keyword

        # Filter jobs using mocked keywords
        filtered_jobs = []
        for job in jobs:
            score = score_job(job, keyword_weights, user_id)
            if score >= SCORE_THRESHOLD:
                filtered_jobs.append({**job, "score": score})

        print(filtered_jobs)


if __name__ == "__main__":
    asyncio.run(main())
