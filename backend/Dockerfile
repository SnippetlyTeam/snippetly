FROM python:3.13-slim-bookworm
# Install uv - dependency manager
COPY --from=ghcr.io/astral-sh/uv:0.8.19 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
ENV PYTHONPATH=/app/src:$PYTHONPATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --locked

# Copy project code
COPY src /app/src

RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Default command runs the API server
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
