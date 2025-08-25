async def block_resources(route):
    """Block images, stylesheets, and fonts to save resources."""
    if route.request.resource_type in ["image", "stylesheet", "font"]:
        await route.abort()
    else:
        await route.continue_()


async def block_pracuj_resources(page):
    """Block images, fonts, and media on Pracuj for optimization."""

    async def route_handler(route):
        if route.request.resource_type in [
            "image",
            "font",
            "media",
        ]:
            await route.abort()
        else:
            await route.continue_()

    await page.route("**/*", route_handler)
