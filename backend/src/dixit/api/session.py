from __future__ import annotations

from flask import session as flask_session

from .errors import NoActiveSessionError


def start_session(game_id: str, player_name: str) -> None:
    flask_session.clear()
    flask_session["game_id"] = game_id
    flask_session["player_name"] = player_name


def end_session() -> None:
    flask_session.clear()


def current_game_id() -> str:
    game_id = flask_session.get("game_id")
    if not game_id:
        raise NoActiveSessionError()
    return game_id


def current_player_name() -> str:
    player_name = flask_session.get("player_name")
    if not player_name:
        raise NoActiveSessionError()
    return player_name
