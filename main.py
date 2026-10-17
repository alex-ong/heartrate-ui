import argparse
import asyncio

from async_utils import await_if_required

from display import DISPLAY_CHOICES, get_display
from scrapers import SCRAPER_CHOICES, get_scraper_class, scan_scraper


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--display", choices=DISPLAY_CHOICES, default="tkinter")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open a browser for the web display",
    )
    parser.add_argument("--scraper", choices=tuple(SCRAPER_CHOICES), default="pulsoid")
    parser.add_argument("--scraper-args", nargs="*", default=[])
    args = parser.parse_args()

    if args.scraper_args and (args.scraper != "bleak" or args.scraper_args != ["scan"]):
        parser.error("--scraper-args currently supports only 'bleak scan'")
    if args.no_browser and args.display != "web":
        parser.error("--no-browser can only be used with --display web")

    async def run_selected_display():
        if args.scraper_args:
            await scan_scraper(args.scraper)
            return

        run_display = get_display(
            args.display, open_browser=not args.no_browser
        )
        scraper = get_scraper_class(args.scraper)()
        try:
            await run_display(scraper)
        finally:
            await await_if_required(scraper.close())

    try:
        asyncio.run(run_selected_display())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
