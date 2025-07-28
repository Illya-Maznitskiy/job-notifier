import json
from pathlib import Path
from typing import List, Dict, Optional

import yaml

from logs.logger import logger


SCORE_THRESHOLD = -2  # Adjust this threshold as needed


def load_keyword_weights(filename="keyword_weights.yaml") -> dict:
    """Load keyword weights from YAML file."""
    # Get root path
    project_root = Path(__file__).resolve().parent.parent
    # Full path to YAML file
    weights_path = project_root / filename

    if not weights_path.exists():
        logger.error(f"Keyword weights not found: {weights_path}")
        raise FileNotFoundError(
            f"Keyword weights file not found: {weights_path}"
        )

    logger.info(f"Loading keyword weights from: {weights_path}")

    # Read and parse YAML
    with open(weights_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        # Combine positive + negative weights
        return {**data.get("positive", {}), **data.get("negative", {})}


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
        keyword_weights = load_keyword_weights()

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

    seen_urls = set()
    filtered_jobs = []
    for job in vacancies:
        url = job.get("url")
        if not url or url in seen_urls:
            logger.debug(f"Duplicate or missing URL skipped: {url}")
            continue
        seen_urls.add(url)

        logger.info(f"Processing job '{job['title']}'")
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
