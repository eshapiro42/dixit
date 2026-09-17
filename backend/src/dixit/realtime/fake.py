from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .rooms import game_room, player_room


@dataclass
class Emission:
    room: str
    event: str
    payload: Any


class FakeBroadcaster:
    """A Broadcaster fake that records emissions instead of sending them anywhere."""

    def __init__(self) -> None:
        self.emissions: list[Emission] = []

    def to_game(self, game_id: str, event: str, payload: Any) -> None:
        self.emissions.append(Emission(room=game_room(game_id), event=event, payload=payload))

    def to_player(self, game_id: str, player_name: str, event: str, payload: Any) -> None:
        room = player_room(game_id, player_name)
        self.emissions.append(Emission(room=room, event=event, payload=payload))
