import pytest
from flask import Flask
from flask.testing import FlaskClient

from dixit.api.errors import register_error_handlers
from dixit.api.notifier import GameNotifier
from dixit.api.routes import build_routes_blueprint
from dixit.domain import CardLibrary
from dixit.realtime import FakeBroadcaster
from dixit.store import GameStore, InMemoryGameStore


@pytest.fixture
def card_library(tmp_path) -> CardLibrary:
    for i in range(60):
        (tmp_path / f"{i}.jpg").write_bytes(b"x")
    return CardLibrary(tmp_path)


@pytest.fixture
def store() -> GameStore:
    return InMemoryGameStore()


@pytest.fixture
def broadcaster() -> FakeBroadcaster:
    return FakeBroadcaster()


@pytest.fixture
def app(store: GameStore, card_library: CardLibrary, broadcaster: FakeBroadcaster) -> Flask:
    flask_app = Flask(__name__)
    flask_app.config.update(SECRET_KEY="test", TESTING=True)
    notifier = GameNotifier(broadcaster)
    blueprint = build_routes_blueprint(store=store, library=card_library, notifier=notifier)
    flask_app.register_blueprint(blueprint)
    register_error_handlers(flask_app)
    return flask_app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


def create_game(client: FlaskClient, player_name: str) -> dict:
    response = client.post("/api/games", json={"player_name": player_name})
    assert response.status_code == 200
    return response.get_json()


def join_game(client: FlaskClient, game_id: str, player_name: str) -> dict:
    response = client.post(f"/api/games/{game_id}/join", json={"player_name": player_name})
    assert response.status_code == 200
    return response.get_json()
