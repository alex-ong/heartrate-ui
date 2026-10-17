from functools import partial

DISPLAY_CHOICES = ("tkinter", "web")


def get_display(name: str, *, open_browser: bool = True):
    if name == "tkinter":
        from .tk_ui import run
    elif name == "web":
        from .web_ui import run

        return partial(run, open_browser=open_browser)
    else:
        raise ValueError(f"Unknown display: {name}")
    return run