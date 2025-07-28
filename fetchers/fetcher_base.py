"""
All fetchers are stored in the "models" directory.
"""

from abc import ABC, abstractmethod

from playwright.async_api import async_playwright, Page

from fetchers.environment import Environment
from fetchers import FetchJob

from fetchers.utils.save_jobs import save_jobs_to_json

from logs.logger import logger

"""


"""
class FetcherBase(ABC):
    service_name: str

    def __init__(self):
        if type(self) is FetcherBase:
            raise TypeError("Can't instantiate abstract class")
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        registered_fetchers.append(cls())

        if not cls.service_name:
            raise RuntimeError("Service name must be defined")

        logger.info(f"Class {cls.__name__}({cls.service_name}) is registered as fetcher.")

    @abstractmethod
    async def fetch(self, page: Page) -> list[FetchJob] | None:
        """
        Abstract method to fetch jobs from a page.
        :param page: Page to fetch jobs from.
        """
        raise NotImplementedError("Abstract method")

    async def execute(self, save_jobs: bool = False) -> list[FetchJob]:
        """
        Executes the scraping process for the specified service.

        Launches a Playwright browser, navigates to the service URL, fetches job listings
        via the `fetch` method, and optionally saves them to a JSON file.

        :param save_jobs: If True, the fetched jobs are saved to a JSON file named after the service.
        :return: A list of FetchJob instances containing the fetched job data.
        """
        logger.info("-" * 60)
        logger.info(f"Launching browser for {self.service_name} scraping")

        url, headless = Environment.load_service(self.service_name)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            page: Page = await browser.new_page()

            logger.info(f"Fetching {self.service_name} page: {url}")
            await page.goto(url)

            try:
                fetched_jobs = await self.fetch(page)

            except Exception as e:
                logger.error(f"Error fetching {self.service_name} page: {url} \n{e}")

            await browser.close()

        logger.info(f"Fetching is done. Total jobs fetched: {len(fetched_jobs)}")

        if save_jobs:
            save_jobs_to_json(fetched_jobs, f"{self.service_name}.json")


        return fetched_jobs



registered_fetchers: list[FetcherBase] = []
