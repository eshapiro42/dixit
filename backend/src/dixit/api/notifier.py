from __future__ import annotations

from dixit.domain import Game, Round
from dixit.realtime import Broadcaster

from . import views


class GameNotifier:
    """Turns a mutated Game into broadcasts, deciding what each room may see."""

    def __init__(self, broadcaster: Broadcaster) -> None:
        self._broadcaster = broadcaster

    def state_changed(self, game: Game) -> None:
        self._broadcaster.to_game(game.id, "state", views.public_view(game))
        for player in game.players:
            if player.is_cpu:
                continue
            payload = views.private_view(game, player)
            self._broadcaster.to_player(game.id, player.name, "you", payload)

    def round_finished(self, game_id: str, finished_round: Round) -> None:
        self._broadcaster.to_game(game_id, "round_outcome", views.round_outcome(finished_round))

    def message(self, game_id: str, text: str, *, emphasis: bool = False) -> None:
        self._broadcaster.to_game(game_id, "message", {"text": text, "emphasis": emphasis})
