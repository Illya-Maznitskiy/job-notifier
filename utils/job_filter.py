import json
from pathlib import Path
from typing import List, Dict, Optional

from logs.logger import logger


# you can manage this data on your own
KEYWORD_WEIGHTS = {
    # Primary job roles
    "python": 5,
    "python developer": 8,
    "junior": 8,
    "junior python": 10,
    "junior software developer": 7,
    "backend python": 7,
    "web developer": 3,
    # Remote work
    "remote": 4,
    "zdalnie": 4,
    "віддалено": 4,
    # Tech / Stack
    "django": 4,
    "fastapi": 3,
    "flask": 3,
    "scrapy": 3,
    "rest api": 2,
    "sql": 2,
    # Multilingual terms (positive)
    "mlodszy": 7,
    "молодший": 7,
    "розробник": 5,
    "розробка": 2,
    "backend": 2,
    # Negative weights: roles to avoid
    "senior": -5,
    "starszy": -5,
    "старший": -5,
    "mid": -2,
    "middle": -2,
    "średni": -2,
    "середній": -2,
    "intern": -2,
    "stażysta": -2,
    "стажер": -2,
    # Unwanted tech
    "fullstack": -3,
    "full stack": -3,
    "javascript": -4,
    "react": -4,
    "vue": -3,
    "frontend": -3,
    "devops": -5,
    "qa": -3,
    "testing": -2,
    "automation": -2,
    # Other unwanted
    "game": -2,
    "android": -3,
    "ios": -3,
}


SCORE_THRESHOLD = -2  # Adjust this threshold as needed


def score_job(job: Dict[str, str], keyword_weights: Dict[str, int]) -> int:
    """
    Score job based on keyword relevance.
    """
    logger.info("-" * 60)

    title = job.get("title", "")
    skills = job.get("skills", "")
    description = job.get("description", "")

    if isinstance(skills, list):
        skills = " ".join(skills)

    combined_text = " ".join([title, skills, description]).lower()

    score = 0
    for keyword, weight in keyword_weights.items():
        count = combined_text.count(keyword)
        if count > 0:
            score += weight * count
            logger.debug(
                f"Matched '{keyword}' {count}x in job: '{title}' "
                f"-> +{weight * count} points"
            )

    logger.debug(f"Total score for job '{title}': {score}")
    return score


def filter_and_score_jobs_from_file(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    keyword_weights: Optional[Dict[str, int]] = None,
    score_threshold: int = SCORE_THRESHOLD,
) -> List[Dict[str, str]]:
    """
    Filter jobs from file by score.
    """
    logger.info("-" * 60)
    logger.info("Filtering jobs")

    if keyword_weights is None:
        keyword_weights = KEYWORD_WEIGHTS

    project_root = Path(__file__).resolve().parent.parent

    if input_path is None:
        input_path = project_root / "storage" / "all_vacancies.json"
    else:
        input_path = Path(input_path)
        if not input_path.is_absolute():
            input_path = project_root / input_path

    if output_path is None:
        output_path = project_root / "storage" / "filtered_vacancies.json"
    else:
        output_path = Path(output_path)
        if not output_path.is_absolute():
            output_path = project_root / output_path

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return []

    with open(input_path, "r", encoding="utf-8") as f:
        vacancies = json.load(f)

    logger.info(f"Loaded {len(vacancies)} jobs from {input_path}")

    filtered_jobs = []
    for job in vacancies:
        logger.info(f"Processing job '{job['title']}")
        score = score_job(job, keyword_weights)
        if score >= score_threshold:
            job["score"] = score
            filtered_jobs.append(job)
            logger.debug(
                f"Job passed: '{job.get('title', '')}' (score: {score})"
            )
        else:
            logger.debug(
                f"Job skipped: '{job.get('title', '')}' (score: {score})"
            )

    filtered_jobs.sort(key=lambda job: job["score"], reverse=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(filtered_jobs, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(filtered_jobs)} filtered jobs to {output_path}")

    return filtered_jobs


if __name__ == "__main__":
    filter_and_score_jobs_from_file()
