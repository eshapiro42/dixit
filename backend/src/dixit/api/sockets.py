from __future__ import annotations

from flask import session
from flask_socketio import SocketIO, join_room

from dixit.realtime import game_room, player_room
from dixit.store import GameStore


def register_socket_handlers(socketio: SocketIO, *, store: GameStore) -> None:
    @socketio.on("connect")
    def handle_connect() -> None:
        game_id = session.get("game_id")
        player_name = session.get("player_name")
        if not game_id or not player_name or not store.exists(game_id):
            return
        join_room(game_room(game_id))
        join_room(player_room(game_id, player_name))
