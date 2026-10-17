import asyncio
import webbrowser
from pathlib import Path

from aiohttp import WSMsgType, web

from async_utils import await_if_required


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_ROOT = Path(__file__).resolve().parent / "static"
FONT_PATH = PROJECT_ROOT / "fonts" / "PressStart2P-Regular.ttf"
HEARTS_ROOT = PROJECT_ROOT / "imgs"
HOST = "127.0.0.1"
PORT = 3939
RATE_INTERVAL = 0.5


class WebDisplay:
    def __init__(self, scraper):
        self.scraper = scraper
        self.rate = 60
        self.clients = set()
        self.app = web.Application()
        self.app.on_shutdown.append(self.shutdown)
        self.app.add_routes(
            [
                web.get("/", self.index),
                web.get("/ws", self.websocket),
                web.get("/assets/font.ttf", self.font),
                web.get("/assets/hearts/{frame}.png", self.heart),
                web.static("/static/", STATIC_ROOT),
            ]
        )

    async def index(self, _request):
        return web.FileResponse(STATIC_ROOT / "index.html")

    async def font(self, _request):
        return web.FileResponse(FONT_PATH)

    async def heart(self, request):
        try:
            frame = int(request.match_info["frame"])
        except ValueError:
            raise web.HTTPNotFound()
        if frame not in range(1, 6):
            raise web.HTTPNotFound()
        return web.FileResponse(HEARTS_ROOT / f"{frame}.png")

    async def websocket(self, request):
        socket = web.WebSocketResponse(heartbeat=30)
        await socket.prepare(request)
        self.clients.add(socket)
        await socket.send_json({"rate": self.rate})
        try:
            async for message in socket:
                if message.type == WSMsgType.ERROR:
                    break
        finally:
            self.clients.discard(socket)
        return socket

    async def shutdown(self, _app):
        clients = tuple(self.clients)
        if clients:
            await asyncio.gather(
                *(
                    socket.close(code=1001, message=b"Server shutting down")
                    for socket in clients
                ),
                return_exceptions=True,
            )
        self.clients.clear()

    async def poll_rates(self):
        while True:
            rate = await await_if_required(self.scraper.get_rate())
            if rate is None:
                for socket in tuple(self.clients):
                    await socket.close(code=1001, message=b"Scraper stopped")
                return

            self.rate = int(rate)
            clients = tuple(self.clients)
            if clients:
                results = await asyncio.gather(
                    *(socket.send_json({"rate": self.rate}) for socket in clients),
                    return_exceptions=True,
                )
                for socket, result in zip(clients, results):
                    if isinstance(result, Exception):
                        self.clients.discard(socket)
            await asyncio.sleep(RATE_INTERVAL)


async def run(scraper, open_browser=True):
    display = WebDisplay(scraper)
    runner = web.AppRunner(display.app)
    url = f"http://{HOST}:{PORT}/"

    try:
        await runner.setup()
        site = web.TCPSite(runner, HOST, PORT)
        await site.start()
        print(f"Web display available at {url}")
        if open_browser and not webbrowser.open_new_tab(url):
            print(f"Open this URL in a browser: {url}")
        await display.poll_rates()
    finally:
        await runner.cleanup()
