FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.8.19 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
ENV PYTHONPATH=/app/src:$PYTHONPATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --locked --group test

COPY src /app/src
COPY tests /app/tests

RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser
