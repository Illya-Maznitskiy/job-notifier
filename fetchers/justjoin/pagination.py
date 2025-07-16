from logs.logger import logger


async def scroll_and_fetch_jobs(page, max_attempts=30):
    """
    Scroll page and fetch job offers asynchronously.
    """
    from fetchers.justjoin.fetcher import (
        parse_job_offer,
    )  # Import here to avoid circular imports

    results = []
    seen_urls = set()
    job_counter = 1

    for i in range(max_attempts):
        await page.evaluate("window.scrollBy(0, 700)")
        await page.wait_for_timeout(1500)

        offers = await page.query_selector_all("a.offer-card")
        current_count = len(offers)
        logger.info(f"Scroll attempt {i + 1}: {current_count} offers")

        # Fetch data for new offers only
        new_offers = []
        for offer in offers:
            job_data = await parse_job_offer(offer)
            if job_data["url"] and job_data["url"] not in seen_urls:
                seen_urls.add(job_data["url"])
                new_offers.append(job_data)

                logger.info(
                    f"{job_counter:>3}. {job_data['title']:<50} @ {job_data['company']}"
                )
                job_counter += 1

        if not new_offers:
            logger.info("No new offers loaded, stopping scroll.")
            break

        # Append new offers to results
        results.extend(new_offers)

    return results
