import asyncio
import tkinter as tk
from tkinter import Frame

from async_utils import await_if_required
from .heart_canvas import HeartCanvas
from .rate_label import RateLabel
from .rate_graph import RateGraph


class Window(Frame):
    def __init__(self, master, scraper):
        Frame.__init__(self, master)
        self.master = master

        self.scraper = scraper
        self._closing = False
        self.closed = asyncio.Event()
        self.config(bg="#000000")

        self.grid(sticky="NSEW")
        self.rate_graph = RateGraph(self)
        self.rate_graph.grid(column=0, row=4)

        self.header = Frame(self, bg="#000000")
        self.header.grid(column=0, row=0, sticky="EW")
        self.header.grid_columnconfigure(0, weight=1)
        self.heart_canvas = HeartCanvas(self.header)
        self.heart_canvas.grid(column=1, row=0, sticky="NE")
        self.rate_label = RateLabel(
            self.header, self.rate_graph.dpi, self.heart_canvas.rate
        )
        self.rate_label.grid(column=0, row=0, sticky="NW")

    async def pump_tk(self):
        while not self._closing:
            try:
                self.master.update()
            except tk.TclError:
                self.close()
                return
            await asyncio.sleep(1 / 60)

    async def pull_data(self):
        while not self._closing:
            value = await await_if_required(self.scraper.get_rate())
            if value is None:
                self.close()
                return
            self.heart_canvas.set_rate(value)
            self.rate_label.set_rate(value)
            self.rate_graph.set_rate(value)
            await asyncio.sleep(0.5)

    def get_async_tasks(self):
        """
        Returns a list of asyncio tasks for the window, and kicks them off.
        """
        return [
            asyncio.create_task(self.pump_tk()),
            asyncio.create_task(self.heart_canvas.animate_heart()),
            asyncio.create_task(self.pull_data()),
        ]

    def close(self):
        if self._closing:
            return
        self._closing = True
        self.closed.set()
        self.master.destroy()


async def run(scraper):
    root = tk.Tk()
    root.title("Heart-Tracker")
    root.config(background="#000000")
    app = Window(root, scraper)
    root.protocol("WM_DELETE_WINDOW", app.close)
    tasks = app.get_async_tasks()
    try:
        await app.closed.wait()
    finally:
        app.close()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
