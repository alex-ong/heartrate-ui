import asyncio
import tkinter as tk

from PIL import Image, ImageTk

from .fonts import get_asset_path


class HeartCanvas(tk.Canvas):
    def __init__(self, master):
        super().__init__(master, width=60, height=52, bg="black", highlightthickness=0)
        self._heart_images = []
        self._hearts = []
        self._rate = 60

        for index in range(1, 6):
            with Image.open(get_asset_path("imgs", f"{index}.png")) as image:
                render = ImageTk.PhotoImage(image)
            self._heart_images.append(render)
            self._hearts.append(self.create_image(0, 0, anchor=tk.NW, image=render))

    @property
    def rate(self):
        return self._rate

    def set_rate(self, rate):
        self._rate = rate

    async def animate_heart(self):
        while True:
            rate = self._rate
            if rate == 0:
                self.animate_step(-1)
                await asyncio.sleep(0.5)
                continue

            order = self.animation_order(self.animation_intensity(rate))
            step_time = 60.0 / rate / len(order)
            for index in order:
                self.animate_step(index)
                await asyncio.sleep(step_time)

    def animate_step(self, index):
        for heart_index, heart in enumerate(self._hearts):
            state = tk.NORMAL if heart_index == index else tk.HIDDEN
            self.itemconfigure(heart, state=state)

    def animation_order(self, max_anim):
        end_count = min(max_anim, len(self._hearts))
        return list(range(end_count)) + list(range(end_count - 2, 0, -1))

    @staticmethod
    def animation_intensity(bpm):
        if bpm < 70:
            return 2
        elif bpm < 100:
            return 3
        elif bpm < 130:
            return 4
        elif bpm < 160:
            return 5
        else:
            return 6
