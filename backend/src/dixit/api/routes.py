from __future__ import annotations

import random
import string

from flask import Blueprint, Response, jsonify, request, send_from_directory

from dixit.domain import MIN_HUMAN_PLAYERS, CardLibrary, DixitError, Game
from dixit.store import GameStore

from . import views
from .notifier import GameNotifier
from .session import current_game_id, current_player_name, end_session, start_session

GAME_ID_ALPHABET = string.ascii_uppercase + string.digits
GAME_ID_LENGTH = 4
MAX_NAME_LENGTH = 32
MAX_PROMPT_LENGTH = 200


def build_routes_blueprint(
    *,
    store: GameStore,
    library: CardLibrary,
    notifier: GameNotifier,
    min_human_players: int = MIN_HUMAN_PLAYERS,
) -> Blueprint:
    """Every handler below follows the same shape: mutate the game inside a store
    transaction (so it's saved before anything is announced), then broadcast.
    """
    bp = Blueprint("api", __name__, url_prefix="/api")

    def json_body() -> dict:
        body = request.get_json(force=True, silent=True)
        if not isinstance(body, dict):
            raise DixitError("Expected a JSON object.")
        return body

    def player_name_from(payload: dict) -> str:
        name = str(payload.get("player_name", "")).strip()[:MAX_NAME_LENGTH]
        if not name:
            raise DixitError("A player name is required.")
        return name

    def card_id_from(payload: dict) -> str:
        card_id = str(payload.get("card_id", "")).strip()
        if not card_id:
            raise DixitError("A card is required.")
        return card_id

    def prompt_from(payload: dict) -> str:
        prompt = str(payload.get("prompt", "")).strip()[:MAX_PROMPT_LENGTH]
        if not prompt:
            raise DixitError("A prompt is required.")
        return prompt

    def require_creator(game: Game, player_name: str) -> None:
        if player_name != game.creator_name:
            raise DixitError("Only the game's creator can do that.")

    def new_game_id() -> str:
        game_id = "".join(random.choices(GAME_ID_ALPHABET, k=GAME_ID_LENGTH))
        while store.exists(game_id):
            game_id = "".join(random.choices(GAME_ID_ALPHABET, k=GAME_ID_LENGTH))
        return game_id

    @bp.post("/games")
    def create_game() -> Response:
        player_name = player_name_from(json_body())
        game_id = new_game_id()
        game = Game.new(
            game_id, library, creator_name=player_name, min_human_players=min_human_players
        )
        game.add_player(player_name)
        store.create(game)
        start_session(game_id, player_name)
        return jsonify(views.session_view(game, player_name))

    @bp.post("/games/<game_id>/join")
    def join_game(game_id: str) -> Response:
        player_name = player_name_from(json_body())
        with store.transaction(game_id) as game:
            rejoining = game.has_player(player_name)
            if not rejoining:
                game.add_player(player_name)
            view = views.session_view(game, player_name)
        start_session(game_id, player_name)
        message = "has rejoined the game." if rejoining else "has joined the game."
        notifier.message(game_id, f"{player_name} {message}")
        if not rejoining:
            notifier.state_changed(game)
        return jsonify(view)

    @bp.get("/session")
    def get_session() -> Response:
        game_id = current_game_id()
        player_name = current_player_name()
        with store.transaction(game_id) as game:
            return jsonify(views.session_view(game, player_name))

    @bp.post("/session/leave")
    def leave_session() -> Response:
        game_id = current_game_id()
        player_name = current_player_name()
        end_session()
        with store.transaction(game_id) as game:
            if game.started or not game.has_player(player_name):
                return jsonify(ok=True)
            game.remove_player(player_name)
        notifier.message(game_id, f"{player_name} left before the game started.")
        notifier.state_changed(game)
        return jsonify(ok=True)

    @bp.post("/session/add-cpu")
    def add_cpu() -> Response:
        game_id = current_game_id()
        player_name = current_player_name()
        with store.transaction(game_id) as game:
            require_creator(game, player_name)
            cpu_name = f"CPU-{game.num_cpu_players + 1}"
            game.add_player(cpu_name, is_cpu=True)
        notifier.message(game_id, f"{cpu_name} has joined the game.")
        notifier.state_changed(game)
        return jsonify(ok=True)

    @bp.post("/session/start")
    def start_game() -> Response:
        game_id = current_game_id()
        player_name = current_player_name()
        with store.transaction(game_id) as game:
            require_creator(game, player_name)
            game.start()
        notifier.message(game_id, "The game has started.", emphasis=True)
        notifier.state_changed(game)
        return jsonify(ok=True)

    @bp.post("/session/host-choice")
    def host_choice() -> Response:
        game_id = current_game_id()
        player_name = current_player_name()
        payload = json_body()
        card_id = card_id_from(payload)
        prompt = prompt_from(payload)
        with store.transaction(game_id) as game:
            player = game.player(player_name)
            scored = game.submit_host_choice(player, card_id, prompt)
            finished_round = game.current_round if scored else None
            if scored:
                game.advance_round()
        notifier.message(game_id, f'{player_name}\'s prompt: "{prompt}"', emphasis=True)
        if finished_round is not None:
            notifier.round_finished(game_id, finished_round)
        notifier.state_changed(game)
        return jsonify(ok=True)

    @bp.post("/session/play")
    def play_card() -> Response:
        game_id = current_game_id()
        player_name = current_player_name()
        card_id = card_id_from(json_body())
        with store.transaction(game_id) as game:
            player = game.player(player_name)
            scored = game.submit_other_choice(player, card_id)
            finished_round = game.current_round if scored else None
            if scored:
                game.advance_round()
        notifier.message(game_id, f"{player_name} played a card.")
        if finished_round is not None:
            notifier.round_finished(game_id, finished_round)
        notifier.state_changed(game)
        return jsonify(ok=True)

    @bp.post("/session/vote")
    def vote() -> Response:
        game_id = current_game_id()
        player_name = current_player_name()
        card_id = card_id_from(json_body())
        with store.transaction(game_id) as game:
            player = game.player(player_name)
            scored = game.submit_vote(player, card_id)
            finished_round = game.current_round if scored else None
            if scored:
                game.advance_round()
        notifier.message(game_id, f"{player_name} voted.")
        if finished_round is not None:
            notifier.round_finished(game_id, finished_round)
        notifier.state_changed(game)
        return jsonify(ok=True)

    @bp.post("/session/mulligan")
    def mulligan() -> Response:
        game_id = current_game_id()
        player_name = current_player_name()
        card_id = card_id_from(json_body())
        with store.transaction(game_id) as game:
            player = game.player(player_name)
            game.submit_mulligan(player, card_id)
        notifier.message(game_id, f"{player_name} used a mulligan.")
        notifier.state_changed(game)
        return jsonify(ok=True)

    @bp.get("/cards/<card_id>")
    def get_card(card_id: str) -> Response:
        return send_from_directory(library.directory, card_id, max_age=60 * 60 * 24 * 365)

    return bp
