import asyncio
import os
from typing import List, Tuple

from dotenv import load_dotenv
from sqlalchemy import select

from db.db import AsyncSessionLocal
from db.models import UserKeyword, Job
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


def score_job(job: Job, keyword_weights: dict, user_id=None) -> int:
    """Score job based on keyword relevance."""
    logger.info("-" * 60)

    title = job.title or ""
    skills = job.skills or ""

    if isinstance(skills, list):
        skills = " ".join(skills)

    combined_text = " ".join([title, skills]).lower()

    score = 0
    for keyword, weight in keyword_weights.items():
        if keyword in combined_text:
            score += weight

    logger.debug(f"Job '{job.title}' scored {score} for user_id={user_id}")
    return score


async def filter_jobs_for_user(
    session, user_id: int, jobs: List[Job]
) -> List[Tuple[Job, int]]:
    """Filter jobs for a single user based on their keywords and compute scores."""
    keyword_weights = await get_user_keywords(session, user_id)

    scored_jobs: List[Tuple[Job, int]] = []
    for job in jobs:
        score = score_job(job, keyword_weights, user_id)
        if score >= SCORE_THRESHOLD:
            scored_jobs.append((job, score))

    # sort by score descending
    scored_jobs.sort(key=lambda x: x[1], reverse=True)
    return scored_jobs  # list of (job, score)


async def main():
    async with AsyncSessionLocal() as session:
        # Mock a job (use Job ORM object, not dict)
        job = Job(
            id=1,
            title="Python Developer",
            company="ABC",
            skills=["python"],  # list is fine if your column is JSON/ARRAY
            url="https://...",
        )

        jobs = [job]

        # Mock user keywords instead of fetching from DB
        user_id = 1
        keyword_weights = {"python": 10}  # pretend the user has this keyword

        # Filter jobs using mocked ORM object
        filtered_jobs = []
        for job in jobs:
            score = score_job(job, keyword_weights, user_id)
            if score >= SCORE_THRESHOLD:
                filtered_jobs.append((job, score))

        print(filtered_jobs)


if __name__ == "__main__":
    asyncio.run(main())
