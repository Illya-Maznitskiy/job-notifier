import asyncio

from fetchers import FetcherBase, FetchJob
from logs.logger import logger
from playwright.async_api import ElementHandle



class FetcherBulldog(FetcherBase):
    service_name = "bulldog"

    async def fetch(self, page) -> list[FetchJob]:
        async def extract(jobHandle: ElementHandle) -> dict:
            job = {}

            title_el = await jobHandle.query_selector("h3")
            if title_el:
                title = await title_el.text_content()
                if title:
                    job["title"] = title.strip()

            url_el = await jobHandle.get_attribute("href")
            if url_el:
                job["url"] = url_el.strip()

            company_el = await jobHandle.query_selector("div.uppercase")
            if company_el:
                company = await company_el.text_content()
                if company:
                    job["company"] = company.strip()

            location_el = await jobHandle.query_selector(
                "div.JobListItem_item__details__sg4tk span.text-xs"
            )
            if location_el:
                location = await location_el.text_content()
                if location:
                    job["location"] = location.strip()

            level_els = await jobHandle.query_selector_all(
                "div.JobListItem_item__details__sg4tk span"
            )
            for el in level_els:
                text = (await el.text_content()).lower()
                if "junior" in text or "mid" in text or "senior" in text:
                    job["level"] = text.strip()
                    break

            salary_el = await jobHandle.query_selector(
                "div.JobListItem_item__salary__OIin6"
            )
            if salary_el:
                salary = await salary_el.text_content()
                if salary:
                    job["salary"] = salary.strip()

            skill_elements = await jobHandle.query_selector_all(
                "div.JobListItem_item__tags__POZkk span"
            )
            skills = [await el.text_content() for el in skill_elements]
            if skills:
                job["skills"] = [s.strip() for s in skills]

            return job
        all_jobs = []

        await page.wait_for_selector("a.JobListItem_item__fYh8y", timeout=5000)
        job_items = await page.query_selector_all("a.JobListItem_item__fYh8y")

        if not job_items:
            raise Exception(f"No job items found on the page. Page url is {page.url}")

        for i, handle in enumerate(job_items, start=1):
            job = await extract(handle)
            if "title" in job and "url" in job:
                all_jobs.append(job)
                logger.info(
                    f"{len(all_jobs):>2}. {job['title']} @ "
                    f"{job.get('company', 'unknown')} "
                    f"({job.get('location', 'unknown')})"
                )
            else:
                logger.warning(
                    f"Skipped job #{i} due to missing title or URL"
                )

        return all_jobs



async def main():
    fetcher = FetcherBulldog()
    jobs = await fetcher.execute(save_jobs=False)


if __name__ == "__main__":
    asyncio.run(main())


