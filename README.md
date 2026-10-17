Requires Python 3.14 and [uv](https://docs.astral.sh/uv/).

Copy and edit `sample.env` -> `.env`

Install dependencies:

```bash
uv sync
uv run --env-file .env python main.py
```

Format code:

```bash
uv run ruff format .
```

Run Ruff lint checks:

```bash
uv run ruff check .
```

To run the web display, which opens in your browser by default:

```bash
uv run --env-file .env python main.py --display web
```

The display is served at `http://127.0.0.1:3939/`. For OBS Browser Source, leave the
server running without opening a browser window:

```bash
uv run --env-file .env python main.py --display web --no-browser
```

It will fail the first time, asking you to install chromedriver.exe and add it to your path.
Follow those instructions

For direct Bluetooth heart-rate monitoring, set `BLEAK_SENSOR_ADDRESS` in `.env` and
run:

```bash
uv run --env-file .env python main.py --scraper bleak
```

To scan for nearby BLE devices and print their names and addresses:

```bash
uv run --env-file .env python main.py --scraper bleak --scraper-args scan
```