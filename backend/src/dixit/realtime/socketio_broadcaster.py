from __future__ import annotations

from typing import Any

from flask_socketio import SocketIO

from .rooms import game_room, player_room


class SocketIOBroadcaster:
    def __init__(self, socketio: SocketIO) -> None:
        self._socketio = socketio

    def to_game(self, game_id: str, event: str, payload: Any) -> None:
        self._socketio.emit(event, payload, to=game_room(game_id))

    def to_player(self, game_id: str, player_name: str, event: str, payload: Any) -> None:
        self._socketio.emit(event, payload, to=player_room(game_id, player_name))
