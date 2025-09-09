import asyncio
import os
from typing import List, Tuple

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.crud.user_keyword import get_user_all_keywords
from src.db.models.job import Job
from logs.logger import logger


load_dotenv()


# Get SCORE_THRESHOLD as an integer, default to 0 if not set
SCORE_THRESHOLD = int(os.getenv("SCORE_THRESHOLD", 0))


def score_job(job: Job, keyword_weights: dict[str, int]) -> int:
    """Score job based on keyword relevance."""
    try:
        title = (job.title or "").lower()
        skills = job.skills or ""
        if isinstance(skills, list):
            skills = " ".join(skills).lower()
        else:
            skills = skills.lower()

        score = 0
        for keyword, weight in keyword_weights.items():
            if keyword in title:
                score += weight
            elif keyword in skills:
                score += weight // 2

        return score
    except Exception as e:
        logger.warning(
            f"Failed to score job '{getattr(job, 'title', None)}': {e}"
        )
        return 0


async def filter_jobs_for_user(
    session: AsyncSession, user_id: int, jobs: List[Job]
) -> List[Tuple[Job, int]]:
    """Filter jobs for a user and compute scores."""
    try:
        logger.info("-" * 60)
        keywords_list = await get_user_all_keywords(session, user_id)
        keyword_weights: dict[str, int] = {
            kw.keyword.lower(): kw.weight for kw in keywords_list
        }

        scored_jobs: List[Tuple[Job, int]] = []
        for job in jobs:
            score = score_job(job, keyword_weights)
            if score > SCORE_THRESHOLD:
                scored_jobs.append((job, score))

        # sort by score descending
        scored_jobs.sort(key=lambda x: x[1], reverse=True)
        logger.info(f"Fetched keywords for user {user_id}: {keyword_weights}")
        logger.info(f"Found {len(scored_jobs)} jobs for user {user_id}")
        return scored_jobs
    except Exception as e:
        logger.warning(f"Failed to filter jobs for user {user_id}: {e}")
        return []


async def main() -> None:
    """Run a mock job scoring example."""
    try:
        # Mock a job (use Job ORM object, not dict)
        job = Job(
            id=1,
            title="Python Developer",
            company="ABC",
            skills=["python"],
            url="https://...",
        )

        jobs = [job]

        # Mock user keywords instead of fetching from DB
        keyword_weights = {"python": 10}

        # Filter jobs using mocked ORM object
        filtered_jobs = []
        for job in jobs:
            score = score_job(job, keyword_weights)
            if score > SCORE_THRESHOLD:
                filtered_jobs.append((job, score))

        print(filtered_jobs)
    except Exception as e:
        logger.warning(f"Failed in mock main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
