from tkinter import Frame

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .fonts import get_matplotlib_font


class RateGraph(Frame):
    def __init__(self, master):
        super().__init__(master, bg="#000000")
        self._data = [60] * 240
        font = get_matplotlib_font()

        self._figure = plt.Figure(
            facecolor="black", edgecolor="black", tight_layout=True, figsize=(4, 2)
        )
        x = np.arange(0, 240, 1)
        axes = self._figure.add_subplot(
            111,
            ybound=(40, 200),
            xbound=(0, 240),
            autoscaley_on=False,
            autoscalex_on=False,
            facecolor="black",
        )
        axes.yaxis.set_label_position("right")
        axes.yaxis.tick_right()
        axes.spines["right"].set_color("red")
        axes.spines["bottom"].set_color("red")
        axes.tick_params(axis="y", colors="red")

        label_count = len(axes.get_yticklabels())
        green_inc = 200 / (label_count - 1)
        for index, label in enumerate(axes.get_yticklabels()):
            label.set_fontproperties(font)
            green_hex = "{:02x}".format(int(15 + green_inc * index))
            label.set_color("#FF" + green_hex + "00")
            label.set_fontsize(12)
        (self._line,) = axes.plot(x, np.sin(x), linewidth=3, color="#FF0000")

        self._canvas = FigureCanvasTkAgg(self._figure, master=self)
        self._canvas.get_tk_widget().grid(column=0, row=0)

    @property
    def dpi(self):
        return self._figure.dpi

    def set_rate(self, rate):
        self._data = self._data[1:]
        self._data.append(rate)
        self._line.set_ydata(self._data)
        self._canvas.draw_idle()
