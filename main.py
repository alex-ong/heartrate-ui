import argparse
import asyncio

from scrapers import SCRAPER_CHOICES, get_scraper_class, scan_scraper


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--display", choices=("tkinter",), default="tkinter")
    parser.add_argument("--scraper", choices=tuple(SCRAPER_CHOICES), default="pulsoid")
    parser.add_argument("--scraper-args", nargs="*", default=[])
    args = parser.parse_args()

    if args.scraper_args and (args.scraper != "bleak" or args.scraper_args != ["scan"]):
        parser.error("--scraper-args currently supports only 'bleak scan'")

    from display.tkinter_display import run as run_tkinter

    async def run_selected_display():
        if args.scraper_args:
            await scan_scraper(args.scraper)
            return
        scraper = get_scraper_class(args.scraper)() 
        await run_tkinter(scraper)

    asyncio.run(run_selected_display())


if __name__ == "__main__":
    main()
