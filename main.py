import argparse
import asyncio
from importlib import import_module

from scrapers import SCRAPER_CHOICES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--display", choices=("tkinter",), default="tkinter")
    parser.add_argument("--scraper", choices=tuple(SCRAPER_CHOICES), default="pulsoid")
    args = parser.parse_args()

    from display.tkinter_display import run as run_tkinter

    displays = {"tkinter": run_tkinter}
    module_name, class_name = SCRAPER_CHOICES[args.scraper]
    scraper_class = getattr(import_module(module_name), class_name)

    async def run_selected_display():
        scraper = scraper_class()
        await displays[args.display](scraper)

    asyncio.run(run_selected_display())


if __name__ == "__main__":
    main()
