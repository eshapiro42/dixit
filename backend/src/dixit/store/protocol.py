from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Protocol

from dixit.domain import Game


class GameStore(Protocol):
    """Where games live between requests, keyed by game id.

    A transaction locks the game for its duration, so two requests acting on the
    same game from different worker processes never interleave their writes.
    """

    def create(self, game: Game) -> None: ...

    def exists(self, game_id: str) -> bool: ...

    def transaction(self, game_id: str) -> AbstractContextManager[Game]:
        """Load the game, yield it for mutation, and save it back on a clean exit.

        Raises GameNotFoundError if no game with this id exists. Nothing is saved
        if the block raises.
        """
        ...
