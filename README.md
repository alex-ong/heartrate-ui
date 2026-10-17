Requires Python 3.14 and [uv](https://docs.astral.sh/uv/).

Copy and edit `sample.env` -> `.env`

Install dependencies:

```bash
uv sync
uv run python main.py
```

It will fail the first time, asking you to install chromedriver.exe and add it to your path.
Follow those instructions