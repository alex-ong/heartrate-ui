import asyncio
import inspect
import tkinter as tk
from tkinter import Frame

import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageDraw, ImageFont, ImageTk


class Window(Frame):
    def __init__(self, master, scraper):
        Frame.__init__(self, master)
        self.master = master
        self.font = self.setup_font()

        self.scraper = scraper
        self._closing = False
        self.closed = asyncio.Event()
        self.config(bg="#000000")
        self.data = [60] * 240

        self.init_window()

        self.header = Frame(self, bg="#000000")
        self.header.grid(column=0, row=0, sticky="EW")
        self.header.grid_columnconfigure(0, weight=1)
        rate_font_size = round(12 * self.fig.dpi / 72)
        self.rate_font = ImageFont.truetype(
            "fonts/PressStart2P-Regular.ttf", rate_font_size
        )
        self.rate_image = self.render_rate(self.get_bpm())
        self.rate_label = tk.Label(
            self.header,
            image=self.rate_image,
            bg="#000000",
        )
        self.rate_label.grid(column=0, row=0, sticky="NW")

        self.heart_canvas = tk.Canvas(
            self.header, width=60, height=52, bg="black", highlightthickness=0
        )
        self.heart_canvas.grid(column=1, row=0, sticky="NE")
        self.hearts = self.setup_hearts(self.heart_canvas)

    def get_bpm(self):
        return self.data[-1]

    def render_rate(self, bpm):
        text = f"{bpm:3}"
        left, top, right, bottom = self.rate_font.getbbox("180")
        image = Image.new("RGB", (right - left, bottom - top), "black")
        ImageDraw.Draw(image).text(
            (-left, -top), text, font=self.rate_font, fill="#ff0000"
        )
        return ImageTk.PhotoImage(image)

    def setup_hearts(self, canvas):
        renders = []
        self.heart_images = []
        for index in range(1, 6):
            image = Image.open(f"imgs/{index}.png")
            render = ImageTk.PhotoImage(image)
            renders.append(render)
            self.heart_images.append(render)
        ids = []

        for render in renders:
            canvas_id = canvas.create_image(0, 0, anchor=tk.NW, image=render)
            ids.append(canvas_id)

        return ids

    def setup_font(self):
        font_path = "fonts/PressStart2P-Regular.ttf"
        return font_manager.FontProperties(fname=font_path)

    def animate_heart_step(self, index):
        for i in range(len(self.hearts)):
            if i == index:
                state = tk.NORMAL
            else:
                state = tk.HIDDEN
            self.heart_canvas.itemconfigure(self.hearts[i], state=state)

    def animation_order(self, max_anim):
        end_count = min(max_anim, len(self.hearts))
        return list(range(end_count)) + list(range(end_count - 2, 0, -1))

    def animation_intensity(self, bpm):
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

    async def pump_tk(self):
        while not self._closing:
            try:
                self.master.update()
            except tk.TclError:
                self.close()
                return
            await asyncio.sleep(1 / 60)

    async def animate_heart(self):
        while not self._closing:
            rate = self.get_bpm()
            if rate == 0:
                self.animate_heart_step(-1)
                await asyncio.sleep(0.5)
                continue

            order = self.animation_order(self.animation_intensity(rate))
            step_time = 60.0 / rate / len(order)
            for index in order:
                if self._closing:
                    return
                self.animate_heart_step(index)
                await asyncio.sleep(step_time)

    async def pull_data(self):
        while not self._closing:
            value = self.scraper.get_rate()
            if inspect.isawaitable(value):
                value = await value
            if value is None:
                self.close()
                return
            self.data = self.data[1:]
            self.data.append(value)
            self.rate_image = self.render_rate(self.get_bpm())
            self.rate_label.config(image=self.rate_image)
            self.line.set_ydata(self.data)
            self.canvas.draw_idle()
            await asyncio.sleep(0.5)

    def close(self):
        if self._closing:
            return
        self._closing = True
        self.closed.set()
        self.master.destroy()

    def init_window(self):
        self.grid(sticky="NSEW")

        self.fig = plt.Figure(
            facecolor="black", edgecolor="black", tight_layout=True, figsize=(4, 2)
        )

        self.x = np.arange(0, 240, 1)

        self.ax = self.fig.add_subplot(
            111,
            ybound=(40, 200),
            xbound=(0, 240),
            autoscaley_on=False,
            autoscalex_on=False,
            facecolor="black",
        )
        self.ax.yaxis.set_label_position("right")
        self.ax.yaxis.tick_right()
        self.ax.spines["right"].set_color("red")
        self.ax.spines["bottom"].set_color("red")
        self.ax.tick_params(axis="y", colors="red")

        label_count = len(self.ax.get_yticklabels())
        green_inc = 200 / (label_count - 1)
        for i, label in enumerate(self.ax.get_yticklabels()):
            label.set_fontproperties(self.font)
            green_hex = "{:02x}".format(int(15 + green_inc * i))
            label.set_color("#FF" + green_hex + "00")
            label.set_fontsize(12)
        (self.line,) = self.ax.plot(
            self.x, np.sin(self.x), linewidth=3, color="#FF0000"
        )

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(column=0, row=4)


async def run(scraper):
    root = tk.Tk()
    root.title("Pulsoid-Tracker")
    root.config(background="#000000")
    app = Window(root, scraper)
    root.protocol("WM_DELETE_WINDOW", app.close)
    tasks = [
        asyncio.create_task(app.pump_tk()),
        asyncio.create_task(app.animate_heart()),
        asyncio.create_task(app.pull_data()),
    ]
    try:
        await app.closed.wait()
    finally:
        app.close()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        close_result = scraper.close()
        if inspect.isawaitable(close_result):
            await close_result
