import tkinter as tk
import time
from tkinter import Frame

import matplotlib.animation as animation
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk


class Window(Frame):
    def __init__(self, master, scraper):
        Frame.__init__(self, master)
        self.master = master
        self.font = self.setup_font()

        self.scraper = scraper
        self.config(bg="#000000")
        self.data = [60] * 240

        self.init_window()

        self.heart_canvas = tk.Canvas(
            self, width=100, height=100, bg="black", highlightthickness=0
        )
        self.heart_canvas.grid(column=0, row=5)
        self.hearts = self.setup_hearts(self.heart_canvas)

        self.start = time.time()
        self.animate_heart()

    def get_bpm(self):
        return self.data[-1]

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

    def animate_heart(self):
        rate = self.get_bpm()
        if rate == 0:
            self.animate_heart_step(-1)
            self.master.after(500, self.animate_heart)
            return

        intensity = self.animation_intensity(rate)

        order = self.animation_order(intensity)
        anim_steps = len(order)
        anim_time = 60.0 / rate
        step_time = int(anim_time / anim_steps * 1000)

        for i, index in enumerate(order):
            self.master.after(
                step_time * (i + 1), lambda index=index: self.animate_heart_step(index)
            )
            if i == anim_steps - 1:
                self.master.after(step_time * (i + 1), self.animate_heart)

    def animate(self, i):
        value = self.scraper.get_rate()
        self.data = self.data[1:]
        self.data.append(value)
        self.line.set_ydata(self.data)
        return (self.line,)

    def close(self):
        if self.ani.event_source is not None:
            self.ani.event_source.stop()
        try:
            self.scraper.close()
        finally:
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

        self.ani = animation.FuncAnimation(
            self.fig, self.animate, np.arange(1, 200), interval=500, blit=False
        )


def run(scraper):
    root = tk.Tk()
    root.title("Pulsoid-Tracker")
    root.config(background="#000000")
    app = Window(root, scraper)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()