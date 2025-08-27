from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

from logs.logger import logger


def build_paginated_url(base_url: str, page_number: int):
    """Appends or updates the 'page' parameter in the URL."""
    logger.info("-" * 60)
    try:
        url_parts = list(urlparse(base_url))
        query = parse_qs(url_parts[4])
        query["page"] = [str(page_number)]
        url_parts[4] = urlencode(query, doseq=True)
        final_url = urlunparse(url_parts)
        logger.info(f"Built URL for page {page_number}: {final_url}")
        return final_url
    except TypeError as e:
        logger.error(f"Error building URL for page {page_number}: {e}")
        return base_url  # fallback
