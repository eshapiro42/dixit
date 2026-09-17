# Dixit backend

Flask + Flask-SocketIO, backed by Redis for game state and cross-worker broadcast.

## Developing

```sh
uv sync
redis-server --daemonize yes

SECRET_KEY=dev-secret \
REDIS_URL=redis://127.0.0.1:6379/0 \
CARDS_DIR=../cards \
uv run gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
  --reload --bind 127.0.0.1:8000 dixit.wsgi:app
```

## Checks

```sh
uv run pytest
uv run ruff check src tests
uv run mypy src
```
