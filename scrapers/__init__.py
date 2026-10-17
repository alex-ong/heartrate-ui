SCRAPER_CHOICES = ("pulsoid", "null", "bleak")


def get_scraper_class(name: str) -> type[object]:
    if name == "pulsoid":
        from .pulsoid.pulsoid_scraper import Scraper
    elif name == "null":
        from .null.null_scraper import Scraper
    elif name == "bleak":
        from .bleak.bleak_scraper import Scraper
    else:
        raise ValueError(f"Unknown scraper: {name}")
    return Scraper


async def scan_scraper(name: str) -> None:
    if name != "bleak":
        raise ValueError(f"Scraper does not support scanning: {name}")

    from .bleak.bleak_scraper import Scraper

    await Scraper.scan()
