from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager

from dixit.domain import Game, GameNotFoundError


class InMemoryGameStore:
    """A GameStore fake: the same load/mutate/save transaction semantics as
    RedisGameStore, including one lock per game rather than a single lock
    shared by every game, so it exercises the same concurrency granularity.
    """

    def __init__(self) -> None:
        self._snapshots: dict[str, dict] = {}
        self._locks: dict[str, threading.Lock] = {}
        self._locks_guard = threading.Lock()

    def create(self, game: Game) -> None:
        with self._lock_for(game.id):
            self._snapshots[game.id] = game.to_dict()

    def exists(self, game_id: str) -> bool:
        return game_id in self._snapshots

    @contextmanager
    def transaction(self, game_id: str) -> Iterator[Game]:
        with self._lock_for(game_id):
            snapshot = self._snapshots.get(game_id)
            if snapshot is None:
                raise GameNotFoundError(game_id)
            game = Game.from_dict(snapshot)
            yield game
            self._snapshots[game_id] = game.to_dict()

    def _lock_for(self, game_id: str) -> threading.Lock:
        with self._locks_guard:
            return self._locks.setdefault(game_id, threading.Lock())
