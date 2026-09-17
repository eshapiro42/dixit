from __future__ import annotations

from flask import Flask, jsonify
from flask.typing import ResponseReturnValue

from dixit.domain import DixitError, GameNotFoundError, PlayerNotFoundError

_NOT_FOUND = (GameNotFoundError, PlayerNotFoundError)


class NoActiveSessionError(Exception):
    def __str__(self) -> str:
        return "No active game session. Join or create a game first."


def _status_code_for(error: Exception) -> int:
    if isinstance(error, NoActiveSessionError):
        return 401
    if isinstance(error, _NOT_FOUND):
        return 404
    return 400


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(DixitError)
    @app.errorhandler(NoActiveSessionError)
    def handle_error(error: Exception) -> ResponseReturnValue:
        response = jsonify(error=str(error))
        response.status_code = _status_code_for(error)
        return response
