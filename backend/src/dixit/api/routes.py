from __future__ import annotations

import random
import re
import string

from flask import Blueprint, Response, jsonify, request, send_from_directory

from dixit.domain import MIN_HUMAN_PLAYERS, CardLibrary, DixitError, Game, Phase
from dixit.store import GameStore

from . import views
from .notifier import GameNotifier
from .session import current_game_id, current_player_name, end_session, start_session

GAME_ID_ALPHABET = string.ascii_uppercase + string.digits
GAME_ID_LENGTH = 4
MAX_NAME_LENGTH = 32
MAX_PROMPT_LENGTH = 200
RESERVED_CPU_NAME = re.compile(r"cpu[\s_-]*\d+", re.IGNORECASE)


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
        if RESERVED_CPU_NAME.fullmatch(name):
            raise DixitError('Names like "CPU 1" are reserved for CPU players.')
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

    def phase_announcement(phase: Phase) -> str | None:
        if phase is Phase.OTHERS_CHOOSING:
            return "Other players, choose a card to match the prompt."
        if phase is Phase.VOTING:
            return "Other players, vote for which card you think matches the prompt."
        return None

    def next_host_text(game: Game) -> str | None:
        round_ = game.current_round
        if round_ is None:
            return None
        return f"It is {round_.host_name}'s turn to choose a card and give a prompt."

    def log_next_host(game: Game) -> None:
        text = next_host_text(game)
        if text is not None:
            game.log(text, round_start=True)

    def announce_next_host(game: Game) -> None:
        text = next_host_text(game)
        if text is not None:
            notifier.message(game.id, text, round_start=True)

    def table_names(game: Game) -> set[str]:
        round_ = game.current_round
        return set(round_.table) if round_ else set()

    def cpus_played_since(game: Game, before: set[str]) -> list[str]:
        round_ = game.current_round
        if round_ is None:
            return []
        return [name for name in round_.table if name not in before and game.player(name).is_cpu]

    def played_message(names: list[str]) -> str | None:
        if not names:
            return None
        if len(names) == 1:
            return f"{names[0]} played a card."
        if len(names) == 2:
            return f"{names[0]} and {names[1]} played cards."
        return f"{', '.join(names[:-1])}, and {names[-1]} played cards."

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
        game.log(f"{player_name} created the game room.")
        game.log("Waiting for players.")
        store.create(game)
        start_session(game_id, player_name)
        notifier.message(game_id, f"{player_name} created the game room.")
        notifier.message(game_id, "Waiting for players.")
        return jsonify(views.session_view(game, player_name))

    @bp.post("/games/<game_id>/join")
    def join_game(game_id: str) -> Response:
        player_name = player_name_from(json_body())
        with store.transaction(game_id) as game:
            rejoining = game.has_player(player_name)
            if not rejoining:
                game.add_player(player_name)
            message = "has rejoined the game." if rejoining else "has joined the game."
            game.log(f"{player_name} {message}")
            view = views.session_view(game, player_name)
        start_session(game_id, player_name)
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
            game.log(f"{player_name} left before the game started.")
        notifier.message(game_id, f"{player_name} left before the game started.")
        notifier.state_changed(game)
        return jsonify(ok=True)

    @bp.post("/session/add-cpu")
    def add_cpu() -> Response:
        game_id = current_game_id()
        player_name = current_player_name()
        with store.transaction(game_id) as game:
            require_creator(game, player_name)
            cpu_name = f"CPU {game.num_cpu_players + 1}"
            game.add_player(cpu_name, is_cpu=True)
            game.log(f"{cpu_name} has joined the game.")
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
            game.log("The game has started.", emphasis=True)
            log_next_host(game)
        notifier.message(game_id, "The game has started.", emphasis=True)
        announce_next_host(game)
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
            before = table_names(game)
            scored = game.submit_host_choice(player, card_id, prompt)
            round_ = game.current_round
            finished_round = round_ if scored else None
            next_phase = round_.phase if round_ and not scored else None
            cpus_played = cpus_played_since(game, before)
            played = played_message(cpus_played)
            game.log(f'{player_name}\'s prompt: "{prompt}"', emphasis=True)
            if played:
                game.log(played)
            announcement = phase_announcement(next_phase) if next_phase else None
            if announcement:
                game.log(announcement)
            if scored:
                game.advance_round()
                log_next_host(game)
        notifier.message(game_id, f'{player_name}\'s prompt: "{prompt}"', emphasis=True)
        if played:
            notifier.message(game_id, played)
        if announcement:
            notifier.message(game_id, announcement)
        if finished_round is not None:
            notifier.round_finished(game_id, finished_round)
            announce_next_host(game)
        notifier.state_changed(game)
        return jsonify(ok=True)

    @bp.post("/session/play")
    def play_card() -> Response:
        game_id = current_game_id()
        player_name = current_player_name()
        card_id = card_id_from(json_body())
        with store.transaction(game_id) as game:
            player = game.player(player_name)
            before = table_names(game)
            phase_before = game.current_round.phase if game.current_round else None
            scored = game.submit_other_choice(player, card_id)
            round_ = game.current_round
            finished_round = round_ if scored else None
            next_phase = round_.phase if round_ and not scored else None
            cpus_played = cpus_played_since(game, before)
            played = played_message(cpus_played)
            game.log(f"{player_name} played a card.")
            if played:
                game.log(played)
            # The phase only changes when the last player plays, so announce on a change.
            announcement = (
                phase_announcement(next_phase)
                if next_phase and next_phase is not phase_before
                else None
            )
            if announcement:
                game.log(announcement)
            if scored:
                game.advance_round()
                log_next_host(game)
        notifier.message(game_id, f"{player_name} played a card.")
        if played:
            notifier.message(game_id, played)
        if announcement:
            notifier.message(game_id, announcement)
        if finished_round is not None:
            notifier.round_finished(game_id, finished_round)
            announce_next_host(game)
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
            game.log(f"{player_name} voted.")
            if scored:
                game.advance_round()
                log_next_host(game)
        notifier.message(game_id, f"{player_name} voted.")
        if finished_round is not None:
            notifier.round_finished(game_id, finished_round)
            announce_next_host(game)
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
            game.log(f"{player_name} used a mulligan.")
        notifier.message(game_id, f"{player_name} used a mulligan.")
        notifier.state_changed(game)
        return jsonify(ok=True)

    @bp.get("/cards/<card_id>")
    def get_card(card_id: str) -> Response:
        return send_from_directory(library.directory, card_id, max_age=60 * 60 * 24 * 365)

    return bp
