from __future__ import annotations

import random
from dataclasses import dataclass, field

from .card import CardLibrary
from .deck import Deck
from .exceptions import (
    DuplicatePlayerNameError,
    GameAlreadyStartedError,
    GameNotStartedError,
    NotEnoughPlayersError,
    PlayerNotFoundError,
    WrongPhaseError,
)
from .player import HAND_SIZE, Player
from .round import Round

MIN_PLAYERS = 4
MIN_HUMAN_PLAYERS = 3


@dataclass
class Game:
    id: str
    deck: Deck
    creator_name: str
    players: list[Player] = field(default_factory=list)
    started: bool = False
    host_order: list[str] = field(default_factory=list)
    host_index: int = 0
    current_round: Round | None = None
    previous_round: Round | None = None
    min_human_players: int = MIN_HUMAN_PLAYERS

    @classmethod
    def new(
        cls,
        game_id: str,
        library: CardLibrary,
        creator_name: str,
        min_human_players: int = MIN_HUMAN_PLAYERS,
    ) -> Game:
        return cls(
            id=game_id,
            deck=Deck.shuffled(library),
            creator_name=creator_name,
            min_human_players=min_human_players,
        )

    @property
    def cpu_players(self) -> list[Player]:
        return [player for player in self.players if player.is_cpu]

    @property
    def human_players(self) -> list[Player]:
        return [player for player in self.players if not player.is_cpu]

    @property
    def num_players(self) -> int:
        return len(self.players)

    @property
    def num_human_players(self) -> int:
        return len(self.human_players)

    @property
    def num_cpu_players(self) -> int:
        return len(self.cpu_players)

    @property
    def playable(self) -> bool:
        return self.num_players >= MIN_PLAYERS and self.num_human_players >= self.min_human_players

    @property
    def host(self) -> Player | None:
        if self.current_round is None:
            return None
        return self.player(self.current_round.host_name)

    def has_player(self, name: str) -> bool:
        return any(player.name == name for player in self.players)

    def player(self, name: str) -> Player:
        for player in self.players:
            if player.name == name:
                return player
        raise PlayerNotFoundError(name, self.id)

    def remove_player(self, name: str) -> None:
        leaving = [player for player in self.players if player.name == name]
        self.players = [player for player in self.players if player.name != name]
        for player in leaving:
            for card in player.hand:
                self.deck.discard(card)

    @property
    def _active_round(self) -> Round:
        if self.current_round is None:
            raise GameNotStartedError(self.id)
        return self.current_round

    def add_player(self, name: str, is_cpu: bool = False) -> Player:
        if self.started:
            raise GameAlreadyStartedError(self.id)
        if self.has_player(name):
            raise DuplicatePlayerNameError(name)
        player = Player(name=name, is_cpu=is_cpu)
        for _ in range(HAND_SIZE):
            player.draw(self.deck)
        self.players.append(player)
        return player

    def start(self) -> None:
        if self.started:
            raise GameAlreadyStartedError(self.id)
        if not self.playable:
            raise NotEnoughPlayersError(MIN_PLAYERS, self.min_human_players)
        humans = self.human_players
        random.shuffle(humans)
        self.host_order = [player.name for player in humans]
        self.host_index = 0
        self.started = True
        self._begin_round()

    def _begin_round(self) -> None:
        self.previous_round = self.current_round
        host_name = self.host_order[self.host_index % len(self.host_order)]
        self.host_index += 1
        self.current_round = Round(host_name=host_name)

    def submit_host_choice(self, player: Player, card_id: str, prompt: str) -> bool:
        """Returns True if the round is now fully scored (see _finish_choosing)."""
        round_ = self._active_round
        round_.host_choice(player, self.deck, card_id, prompt)
        return self._finish_choosing(round_)

    def submit_other_choice(self, player: Player, card_id: str) -> bool:
        """Returns True if the round is now fully scored (see _finish_choosing)."""
        round_ = self._active_round
        round_.other_choice(player, self.deck, card_id)
        return self._finish_choosing(round_)

    def submit_mulligan(self, player: Player, card_id: str) -> None:
        self._active_round.mulligan(player, self.deck, card_id)

    def submit_vote(self, player: Player, card_id: str) -> bool:
        """Returns True if every human has now voted, and the round has been scored."""
        round_ = self._active_round
        round_.vote(player, card_id)
        return self._finish_voting(round_)

    def _finish_choosing(self, round_: Round) -> bool:
        """Resolves CPU choices once every human has played, then tries to finish
        voting immediately too: with no other human around to vote either (the
        host is the only human in the game), nothing else will ever trigger it.
        """
        if not round_.all_humans_played(self.human_players):
            return False
        round_.resolve_cpu_choices(self.cpu_players, self.deck)
        return self._finish_voting(round_)

    def _finish_voting(self, round_: Round) -> bool:
        if not round_.all_humans_voted(self.human_players):
            return False
        round_.resolve_cpu_votes(self.cpu_players)
        round_.score(self.players)
        for card in round_.table.values():
            self.deck.discard(card)
        return True

    def advance_round(self) -> None:
        if not self._active_round.is_scored:
            raise WrongPhaseError("advance to the next round", self._active_round.phase.value)
        self._begin_round()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "deck": self.deck.to_dict(),
            "creator_name": self.creator_name,
            "players": [player.to_dict() for player in self.players],
            "started": self.started,
            "host_order": list(self.host_order),
            "host_index": self.host_index,
            "current_round": self.current_round.to_dict() if self.current_round else None,
            "previous_round": self.previous_round.to_dict() if self.previous_round else None,
            "min_human_players": self.min_human_players,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Game:
        return cls(
            id=data["id"],
            deck=Deck.from_dict(data["deck"]),
            creator_name=data["creator_name"],
            players=[Player.from_dict(player) for player in data["players"]],
            started=data["started"],
            host_order=list(data["host_order"]),
            host_index=data["host_index"],
            current_round=Round.from_dict(data["current_round"]) if data["current_round"] else None,
            previous_round=(
                Round.from_dict(data["previous_round"]) if data["previous_round"] else None
            ),
            min_human_players=data["min_human_players"],
        )
