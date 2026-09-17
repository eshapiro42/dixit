from __future__ import annotations

import redis
from flask import Flask
from flask_socketio import SocketIO

from dixit.config import Config
from dixit.domain import CardLibrary
from dixit.realtime import SocketIOBroadcaster
from dixit.store import RedisGameStore

from .errors import register_error_handlers
from .notifier import GameNotifier
from .routes import build_routes_blueprint
from .sockets import register_socket_handlers


def create_app(config: Config | None = None) -> Flask:
    config = config or Config.from_env()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.secret_key

    library = CardLibrary(config.cards_dir)
    store = RedisGameStore(redis.Redis.from_url(config.redis_url))
    socketio = SocketIO(app, message_queue=config.redis_url)
    notifier = GameNotifier(SocketIOBroadcaster(socketio))

    app.register_blueprint(build_routes_blueprint(store=store, library=library, notifier=notifier))
    register_socket_handlers(socketio, store=store)
    register_error_handlers(app)

    @app.get("/healthz")
    def healthz() -> tuple[str, int]:
        return "ok", 200

    app.extensions["socketio"] = socketio
    return app
