import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--display", choices=("tkinter",), default="tkinter")
    parser.add_argument("--scraper", choices=("pulsoid",), default="pulsoid")
    args = parser.parse_args()

    from display.tkinter_display import run as run_tkinter
    from scrapers.pulsoid.pulsoid_scraper import Scraper

    displays = {"tkinter": run_tkinter}
    scrapers = {"pulsoid": Scraper}
    displays[args.display](scrapers[args.scraper]())


if __name__ == "__main__":
    main()
