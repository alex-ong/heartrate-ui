import tkinter as tk

from PIL import Image, ImageDraw, ImageTk

from .fonts import get_pillow_font


class RateLabel(tk.Label):
    def __init__(self, master, dpi, rate):
        font_size = round(12 * dpi / 72)
        self._font = get_pillow_font(font_size)
        self._image = self._render(rate)
        super().__init__(master, image=self._image, bg="#000000")

    def set_rate(self, rate):
        self._image = self._render(rate)
        self.configure(image=self._image)

    def _render(self, rate):
        text = f"{rate:3}"
        left, top, right, bottom = self._font.getbbox("180")
        image = Image.new("RGB", (right - left, bottom - top), "black")
        ImageDraw.Draw(image).text((-left, -top), text, font=self._font, fill="#ff0000")
        return ImageTk.PhotoImage(image)
