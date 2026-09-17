# Dixit

A web implementation of the [Dixit](https://en.wikipedia.org/wiki/Dixit_(card_game)) card game. One player tells a story or gives a clue for a card in their hand, everyone else tries to match it, and points go to whoever's guesses land in the sweet spot between too obvious and too obscure.

## Architecture

- `backend/` — Flask + Flask-SocketIO (Python 3.13, managed with [uv](https://docs.astral.sh/uv/)). Game rules live in a plain domain layer with no framework dependencies; a Redis-backed store and a Socket.IO broadcaster sit behind small protocols so either can be swapped or faked in tests.
- `frontend/` — a SvelteKit static SPA (TypeScript, managed with [pnpm](https://pnpm.io/)) talking to the backend over a JSON API and a Socket.IO connection.
- `caddy/` — reverse proxy in front of both. In production it also serves the built frontend directly.
- `cards/` — the deck's card art.

See `backend/README.md` and `frontend/README.md` for details on each.

## Running locally

```sh
docker compose up --build
```

Then open http://localhost:8080. Add a couple of CPU players and go through the lobby to try a full round without a party.

Set `MIN_HUMAN_PLAYERS=1` in `.env` (or the environment) to drop the three-human minimum for solo testing — CPUs can fill the rest of the table.

## Testing

```sh
cd backend && uv run pytest
cd frontend && pnpm test
```

## Production

```sh
cp .env.example .env   # fill in SECRET_KEY
docker compose -f compose.production.yaml up --build -d
```

This builds the frontend into a static bundle that Caddy serves directly, rather than running a Vite dev server.
