FROM ghcr.io/astral-sh/uv:0.12.3 AS uv
FROM python:3.13-slim AS base

COPY --from=uv /uv /usr/local/bin/uv

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CARDS_DIR=/app/cards

RUN groupadd --gid 1000 app && useradd --uid 1000 --gid app --create-home app \
    && mkdir -p /app /opt/venv && chown app:app /app /opt/venv
WORKDIR /app
USER app

EXPOSE 8000
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=12 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz', timeout=2)"]

FROM base AS dev

COPY --chown=app:app backend/pyproject.toml backend/uv.lock ./
RUN uv sync --locked --all-groups --no-install-project
COPY --chown=app:app backend/ .
COPY --chown=app:app cards/ ./cards/
RUN uv sync --locked --all-groups

CMD ["gunicorn", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", \
     "--reload", "--bind", "0.0.0.0:8000", "dixit.wsgi:app"]

# Keep runtime last: it is the default target when callers omit --target.
FROM base AS runtime

COPY --chown=app:app backend/pyproject.toml backend/uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY --chown=app:app backend/ .
COPY --chown=app:app cards/ ./cards/
RUN uv sync --locked --no-dev

CMD ["gunicorn", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", \
     "-w", "4", "--bind", "0.0.0.0:8000", "dixit.wsgi:app"]
