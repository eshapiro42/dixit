from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager

import redis

from dixit.domain import Game, GameNotFoundError

DEFAULT_TTL_SECONDS = 60 * 60 * 12


class RedisGameStore:
    """A game's lifetime is capped at ttl_seconds since its last write, so an
    abandoned game is reclaimed instead of living in Redis forever.
    """

    def __init__(self, client: redis.Redis, *, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        self._client = client
        self._ttl_seconds = ttl_seconds

    def create(self, game: Game) -> None:
        self._save(game)

    def exists(self, game_id: str) -> bool:
        return bool(self._client.exists(self._key(game_id)))

    @contextmanager
    def transaction(self, game_id: str) -> Iterator[Game]:
        with self._client.lock(self._lock_key(game_id), timeout=10, blocking_timeout=5):
            game = self._load(game_id)
            yield game
            self._save(game)

    def _load(self, game_id: str) -> Game:
        raw = self._client.get(self._key(game_id))
        if raw is None:
            raise GameNotFoundError(game_id)
        return Game.from_dict(json.loads(raw))

    def _save(self, game: Game) -> None:
        self._client.set(self._key(game.id), json.dumps(game.to_dict()), ex=self._ttl_seconds)

    @staticmethod
    def _key(game_id: str) -> str:
        return f"dixit:game:{game_id}"

    @staticmethod
    def _lock_key(game_id: str) -> str:
        return f"dixit:game-lock:{game_id}"
