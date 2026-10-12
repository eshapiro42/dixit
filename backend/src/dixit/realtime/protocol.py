from __future__ import annotations

from typing import Any, Protocol


class Broadcaster(Protocol):
    """Pushes events to connected clients. Domain code never sees this: only the
    API layer, after a mutation has been saved, decides what to broadcast.
    """

    def to_game(self, game_id: str, event: str, payload: Any) -> None: ...

    def to_player(self, game_id: str, player_name: str, event: str, payload: Any) -> None: ...
