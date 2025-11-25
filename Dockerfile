# syntax=docker/dockerfile:1.7

FROM python:3.13-slim AS base

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libx11-6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

FROM base AS deps
WORKDIR /deps

RUN --mount=type=cache,target=/deps/.pip \
    pip install uv --cache-dir /deps/.pip

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/deps/.uv \
    uv sync --frozen --cache-dir /deps/.uv --no-dev --link-mode=hardlink

FROM base AS runtime
WORKDIR /app

RUN --mount=type=cache,target=/deps/.pip \
    pip install uv --cache-dir /deps/.pip

COPY --from=deps /deps/.venv /app/.venv
COPY . /app

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "-s", "main.py", "--no-dev"]
