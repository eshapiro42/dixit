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
    # Explicit rather than relying on browsers' own SameSite-by-default behavior.
    # Not Secure: this app isn't guaranteed to be served over HTTPS.
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    library = CardLibrary(config.cards_dir)
    store = RedisGameStore(redis.Redis.from_url(config.redis_url))
    # Behind TLS-terminating proxies the app sees plain http, so the default
    # same-origin check rejects https browsers; ALLOWED_ORIGINS names them.
    socketio = SocketIO(
        app,
        message_queue=config.redis_url,
        # None (the default) means same-origin only; the type stubs omit it.
        cors_allowed_origins=list(config.allowed_origins) or None,  # type: ignore[arg-type]
    )
    notifier = GameNotifier(SocketIOBroadcaster(socketio))

    blueprint = build_routes_blueprint(
        store=store,
        library=library,
        notifier=notifier,
        min_human_players=config.min_human_players,
    )
    app.register_blueprint(blueprint)
    register_socket_handlers(socketio, store=store)
    register_error_handlers(app)

    @app.get("/healthz")
    def healthz() -> tuple[str, int]:
        return "ok", 200

    app.extensions["socketio"] = socketio
    return app
