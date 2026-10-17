from pathlib import Path

import matplotlib.font_manager as font_manager
from PIL import ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FONT_PATH = PROJECT_ROOT / "fonts" / "PressStart2P-Regular.ttf"


def get_matplotlib_font():
    return font_manager.FontProperties(fname=FONT_PATH)


def get_pillow_font(size):
    return ImageFont.truetype(str(FONT_PATH), size)


def get_asset_path(*parts):
    return PROJECT_ROOT.joinpath(*parts)
