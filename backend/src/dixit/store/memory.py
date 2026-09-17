from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager

from dixit.domain import Game, GameNotFoundError


class InMemoryGameStore:
    """A GameStore fake: the same load/mutate/save transaction semantics as
    RedisGameStore, with no external dependency and nothing surviving the process.
    """

    def __init__(self) -> None:
        self._snapshots: dict[str, dict] = {}
        self._lock = threading.Lock()

    def create(self, game: Game) -> None:
        with self._lock:
            self._snapshots[game.id] = game.to_dict()

    def exists(self, game_id: str) -> bool:
        with self._lock:
            return game_id in self._snapshots

    @contextmanager
    def transaction(self, game_id: str) -> Iterator[Game]:
        with self._lock:
            snapshot = self._snapshots.get(game_id)
            if snapshot is None:
                raise GameNotFoundError(game_id)
            game = Game.from_dict(snapshot)
            yield game
            self._snapshots[game_id] = game.to_dict()
