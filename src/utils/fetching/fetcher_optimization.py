from playwright.async_api import Route, Page

from logs.logger import logger


async def block_resources(route: Route) -> None:
    """Block images, stylesheets, and fonts to save resources."""
    try:
        if route.request.resource_type in ["image", "stylesheet", "font"]:
            await route.abort()
        else:
            await route.continue_()
    except Exception as e:
        logger.warning(f"Route handling failed: {e}")


async def block_pracuj_resources(page: Page) -> None:
    """Block images, fonts, and media on Pracuj for optimization."""

    async def route_handler(route: Route) -> None:
        """Handle Pracuj route requests and block unnecessary resources."""
        try:
            if route.request.resource_type in ["image", "font", "media"]:
                await route.abort()
            else:
                await route.continue_()
        except Exception as e:
            logger.warning(f"Pracuj route handling failed: {e}")

    await page.route("**/*", route_handler)
