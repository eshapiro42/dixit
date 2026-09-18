from conftest import create_game, join_game
from flask import Flask

from dixit.api.errors import register_error_handlers
from dixit.api.notifier import GameNotifier
from dixit.api.routes import build_routes_blueprint
from dixit.realtime import FakeBroadcaster
from dixit.store import InMemoryGameStore


def test_create_game_returns_a_session_view(client) -> None:
    view = create_game(client, "alice")
    assert view["player_name"] == "alice"
    assert view["is_creator"] is True
    assert view["started"] is False
    assert len(view["hand"]) == 6


def test_create_game_requires_a_player_name(client) -> None:
    response = client.post("/api/games", json={"player_name": "  "})
    assert response.status_code == 400


def test_join_game_adds_a_second_player(app: Flask, client) -> None:
    created = create_game(client, "alice")
    bob = app.test_client()
    view = join_game(bob, created["game_id"], "bob")
    assert view["is_creator"] is False
    state = client.get("/api/session").get_json()
    assert {p["name"] for p in state["players"]} == {"alice", "bob"}


def test_join_unknown_game_returns_404(client) -> None:
    response = client.post("/api/games/NOPE/join", json={"player_name": "alice"})
    assert response.status_code == 404


def test_rejoining_does_not_duplicate_the_player(app: Flask) -> None:
    creator = app.test_client()
    created = create_game(creator, "alice")
    bob_first_session = app.test_client()
    join_game(bob_first_session, created["game_id"], "bob")

    bob_new_tab = app.test_client()
    view = join_game(bob_new_tab, created["game_id"], "bob")
    assert view["player_name"] == "bob"

    state = creator.get("/api/session").get_json()
    assert len(state["players"]) == 2


def test_session_requires_an_active_session(client) -> None:
    response = client.get("/api/session")
    assert response.status_code == 401


def test_add_cpu_appears_in_players(app: Flask) -> None:
    creator = app.test_client()
    create_game(creator, "alice")
    response = creator.post("/api/session/add-cpu")
    assert response.status_code == 200
    state = creator.get("/api/session").get_json()
    assert any(p["is_cpu"] for p in state["players"])


def test_start_requires_four_players(app: Flask) -> None:
    creator = app.test_client()
    create_game(creator, "alice")
    response = creator.post("/api/session/start")
    assert response.status_code == 400


def test_start_requires_the_creator(app: Flask) -> None:
    creator = app.test_client()
    created = create_game(creator, "alice")
    bob = app.test_client()
    join_game(bob, created["game_id"], "bob")

    response = bob.post("/api/session/start")
    assert response.status_code == 400


def test_add_cpu_requires_the_creator(app: Flask) -> None:
    creator = app.test_client()
    created = create_game(creator, "alice")
    bob = app.test_client()
    join_game(bob, created["game_id"], "bob")

    response = bob.post("/api/session/add-cpu")
    assert response.status_code == 400


def test_a_non_object_json_body_is_a_clean_400(app: Flask) -> None:
    creator = app.test_client()
    create_game(creator, "alice")

    response = creator.post("/api/session/mulligan", json=None)
    assert response.status_code == 400

    response = creator.post("/api/session/mulligan", json=[1, 2, 3])
    assert response.status_code == 400


def test_a_prompt_over_the_length_limit_is_truncated(app: Flask) -> None:
    lobby = _started_lobby(app)
    clients = lobby["clients"]
    host_name, host = _current_host(clients)
    hand = host.get("/api/session").get_json()["hand"]

    response = host.post("/api/session/host-choice", json={"card_id": hand[0], "prompt": "x" * 500})
    assert response.status_code == 200
    state = host.get("/api/session").get_json()
    assert state["prompt"] is not None
    assert len(state["prompt"]) == 200


def _started_lobby(app: Flask) -> dict[str, object]:
    creator = app.test_client()
    created = create_game(creator, "alice")
    bob = app.test_client()
    join_game(bob, created["game_id"], "bob")
    carol = app.test_client()
    join_game(carol, created["game_id"], "carol")
    creator.post("/api/session/add-cpu")
    creator.post("/api/session/start")
    clients = {"alice": creator, "bob": bob, "carol": carol}
    return {"game_id": created["game_id"], "clients": clients}


def _current_host(clients: dict) -> tuple[str, object]:
    any_client = next(iter(clients.values()))
    state = any_client.get("/api/session").get_json()
    host_name = state["host"]
    return host_name, clients[host_name]


def test_a_full_round_reaches_scoring_and_starts_the_next(app: Flask) -> None:
    lobby = _started_lobby(app)
    clients = lobby["clients"]
    host_name, host = _current_host(clients)
    others = [c for name, c in clients.items() if name != host_name]

    host_hand = host.get("/api/session").get_json()["hand"]
    response = host.post(
        "/api/session/host-choice", json={"card_id": host_hand[0], "prompt": "a memory"}
    )
    assert response.status_code == 200

    played_card_ids = {}
    for other in others:
        assert other.get("/api/session").get_json()["has_played"] is False
        hand = other.get("/api/session").get_json()["hand"]
        played_card_ids[other] = hand[0]
        response = other.post("/api/session/play", json={"card_id": hand[0]})
        assert response.status_code == 200
        assert other.get("/api/session").get_json()["has_played"] is True

    state = host.get("/api/session").get_json()
    assert state["phase"] == "voting"
    assert len(state["table"]) >= 2

    for other in others:
        table = other.get("/api/session").get_json()["table"]
        vote_for = next(card_id for card_id in table if card_id != played_card_ids[other])
        response = other.post("/api/session/vote", json={"card_id": vote_for})
        assert response.status_code == 200

    final_state = host.get("/api/session").get_json()
    assert final_state["phase"] == "host_choosing"
    assert final_state["previous_round_outcome"]["host"] == host_name


def test_cannot_vote_for_your_own_card(app: Flask) -> None:
    lobby = _started_lobby(app)
    clients = lobby["clients"]
    host_name, host = _current_host(clients)
    others = [c for name, c in clients.items() if name != host_name]

    host_hand = host.get("/api/session").get_json()["hand"]
    host.post("/api/session/host-choice", json={"card_id": host_hand[0], "prompt": "a memory"})

    voter = others[0]
    voter_hand = voter.get("/api/session").get_json()["hand"]
    played_card_id = voter_hand[0]
    voter.post("/api/session/play", json={"card_id": played_card_id})
    for other in others[1:]:
        hand = other.get("/api/session").get_json()["hand"]
        other.post("/api/session/play", json={"card_id": hand[0]})

    response = voter.post("/api/session/vote", json={"card_id": played_card_id})
    assert response.status_code == 400


def test_mulligan_replaces_the_hosts_card(app: Flask) -> None:
    lobby = _started_lobby(app)
    clients = lobby["clients"]
    host_name, host = _current_host(clients)

    before = host.get("/api/session").get_json()
    assert before["mulligan_available"] is True
    card_id = before["hand"][0]

    response = host.post("/api/session/mulligan", json={"card_id": card_id})
    assert response.status_code == 200

    after = host.get("/api/session").get_json()
    assert card_id not in after["hand"]
    assert after["mulligan_available"] is False


def test_mulligan_twice_is_rejected(app: Flask) -> None:
    lobby = _started_lobby(app)
    clients = lobby["clients"]
    _, host = _current_host(clients)

    hand = host.get("/api/session").get_json()["hand"]
    host.post("/api/session/mulligan", json={"card_id": hand[0]})
    hand_now = host.get("/api/session").get_json()["hand"]
    response = host.post("/api/session/mulligan", json={"card_id": hand_now[0]})
    assert response.status_code == 400


def test_get_card_serves_the_image(app: Flask, client, card_library) -> None:
    any_card = card_library.cards[0]
    response = client.get(f"/api/cards/{any_card.id}")
    assert response.status_code == 200


def test_get_card_404s_for_an_unknown_card(client) -> None:
    response = client.get("/api/cards/does-not-exist.jpg")
    assert response.status_code == 404


def test_get_card_rejects_path_traversal(client) -> None:
    response = client.get("/api/cards/..%2F..%2Fpyproject.toml")
    assert response.status_code in (400, 404)


def test_joining_broadcasts_state_and_a_message(app: Flask, broadcaster) -> None:
    creator = app.test_client()
    created = create_game(creator, "alice")
    broadcaster.emissions.clear()

    bob = app.test_client()
    join_game(bob, created["game_id"], "bob")

    events = [emission.event for emission in broadcaster.emissions]
    assert "message" in events
    assert "state" in events
    assert "you" in events


def test_min_human_players_is_configurable(card_library) -> None:
    flask_app = Flask(__name__)
    flask_app.config.update(SECRET_KEY="test", TESTING=True)
    notifier = GameNotifier(FakeBroadcaster())
    blueprint = build_routes_blueprint(
        store=InMemoryGameStore(), library=card_library, notifier=notifier, min_human_players=1
    )
    flask_app.register_blueprint(blueprint)
    register_error_handlers(flask_app)

    solo = flask_app.test_client()
    create_game(solo, "alice")
    for _ in range(3):
        solo.post("/api/session/add-cpu")

    response = solo.post("/api/session/start")
    assert response.status_code == 200

    state = solo.get("/api/session").get_json()
    assert state["host"] == "alice"
    response = solo.post(
        "/api/session/host-choice", json={"card_id": state["hand"][0], "prompt": "a memory"}
    )
    assert response.status_code == 200

    after = solo.get("/api/session").get_json()
    assert after["phase"] == "host_choosing"
    assert after["previous_round_outcome"]["host"] == "alice"


def test_leaving_before_start_removes_the_player_and_clears_the_session(app: Flask) -> None:
    creator = app.test_client()
    created = create_game(creator, "alice")
    bob = app.test_client()
    join_game(bob, created["game_id"], "bob")

    response = bob.post("/api/session/leave")
    assert response.status_code == 200

    assert bob.get("/api/session").status_code == 401
    state = creator.get("/api/session").get_json()
    assert {p["name"] for p in state["players"]} == {"alice"}


def test_leaving_after_start_only_clears_the_session(app: Flask) -> None:
    lobby = _started_lobby(app)
    clients = lobby["clients"]
    _, bob = list(clients.items())[1]

    response = bob.post("/api/session/leave")
    assert response.status_code == 200
    assert bob.get("/api/session").status_code == 401

    creator = clients["alice"]
    state = creator.get("/api/session").get_json()
    assert {p["name"] for p in state["players"]} == {"alice", "bob", "carol", "CPU-1"}


def test_leave_requires_an_active_session(client) -> None:
    response = client.post("/api/session/leave")
    assert response.status_code == 401


def test_solo_game_log_covers_the_full_round_lifecycle(card_library) -> None:
    flask_app = Flask(__name__)
    flask_app.config.update(SECRET_KEY="test", TESTING=True)
    broadcaster = FakeBroadcaster()
    notifier = GameNotifier(broadcaster)
    blueprint = build_routes_blueprint(
        store=InMemoryGameStore(), library=card_library, notifier=notifier, min_human_players=1
    )
    flask_app.register_blueprint(blueprint)
    register_error_handlers(flask_app)

    solo = flask_app.test_client()
    create_game(solo, "alice")
    for _ in range(3):
        solo.post("/api/session/add-cpu")
    solo.post("/api/session/start")

    state = solo.get("/api/session").get_json()
    solo.post("/api/session/host-choice", json={"card_id": state["hand"][0], "prompt": "a memory"})

    texts = [e.payload["text"] for e in broadcaster.emissions if e.event == "message"]
    assert "alice created the game room." in texts
    assert "Waiting for players." in texts
    assert sum(text.endswith("has joined the game.") for text in texts) == 3
    assert "The game has started." in texts
    assert texts.count("It is alice's turn to choose a card and give a prompt.") == 2
    assert 'alice\'s prompt: "a memory"' in texts
    assert sum(text.endswith("played a card.") for text in texts) == 3

    after = solo.get("/api/session").get_json()
    outcome = after["previous_round_outcome"]
    assert outcome["host"] == "alice"
    assert set(outcome["votes"]).issubset({"CPU-1", "CPU-2", "CPU-3"})
    assert len(outcome["votes"]) == 3
