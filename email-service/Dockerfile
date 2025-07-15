FROM python:3.13-alpine

WORKDIR /app

COPY pyproject.toml uv.lock /app/
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PATH="/app/.venv/bin:$PATH"
RUN uv sync

COPY . .

CMD ["uv", "run", "src/main.py"]
