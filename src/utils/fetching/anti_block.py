import random
import asyncio


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
]

PROXIES = [
    None,  # No proxy sometimes (less suspicious)
    "http://api.proxyscrape.com/?request=displayproxies&proxytype=http",  # ProxyScrape API
]


async def random_wait(min_sec: float = 1.0, max_sec: float = 5.0):
    """Wait a random time between requests."""
    delay = random.uniform(min_sec, max_sec)
    await asyncio.sleep(delay)


def get_random_user_agent() -> str:
    """Pick a random User-Agent string."""
    return random.choice(USER_AGENTS)


def get_random_proxy() -> str | None:
    """Pick a random proxy (sometimes None for direct)."""
    return random.choice(PROXIES)
