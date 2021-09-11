from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.font_manager as font_manager
from pulsoid_scraper import Scraper

from tkinter import Frame, Label, Entry, Button


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.font = self.setup_font()
        self.scraper = Scraper()
        self.config(bg="#000000")
        self.data = [0]*240
        self.init_window()

    def setup_font(self):
        # the location of the font file
        font_path = "fonts/PressStart2P-Regular.ttf"
        return font_manager.FontProperties(fname=font_path)

    def animate(self, i):
        value = self.scraper.get_rate()
        print(value)
        self.data = self.data[1:]
        self.data.append(value)
        self.line.set_ydata(self.data)  # update the data
        return (self.line,)

    def init_window(self):

        self.grid(sticky="NSEW")
        # Create the controls, note use of grid
        
        self.fig = plt.Figure(
            facecolor="black", edgecolor="black", tight_layout=True, figsize=(4, 2)
        )

        self.x = np.arange(0, 240, 1)  # x-array

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
            print(green_hex)
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


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Pulsoid-Tracker")
    root.config(background="#000000")
    app = Window(root)
    tk.mainloop()
