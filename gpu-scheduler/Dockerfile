FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ADD . /app
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
RUN uv sync --locked
CMD ["uv", "run", "main.py"]
