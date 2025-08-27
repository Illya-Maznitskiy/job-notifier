import random
import asyncio
import httpx

from logs.logger import logger

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
]


async def random_wait(min_sec: float = 1.0, max_sec: float = 5.0):
    """Wait a random time between requests."""
    delay = random.uniform(min_sec, max_sec)
    formatted_delay = str(delay)[:5]
    logger.info(f"Waiting {formatted_delay} seconds...")
    await asyncio.sleep(delay)


def get_random_user_agent() -> str:
    """Pick a random User-Agent string."""
    return random.choice(USER_AGENTS)


async def fetch_proxies() -> list[str]:
    """Fetch a list of working proxies from ProxyScrape."""
    # CAN BE ISSUES WITH THAT FREE OPTION!!!
    url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            proxies = [
                f"http://{p}" for p in resp.text.splitlines() if p.strip()
            ]
            logger.info(f"Fetched {len(proxies)} proxies from ProxyScrape")
            return proxies
    except Exception as e:
        logger.warning(f"Failed to fetch proxies: {e}")
        return []


async def get_random_proxy() -> str | None:
    """Return a random proxy or None."""
    if random.random() < 0.3:  # 30% of the time, go direct
        return None
    proxies = await fetch_proxies()
    return random.choice(proxies) if proxies else None
