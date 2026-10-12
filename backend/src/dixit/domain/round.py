from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum

from .card import Card
from .deck import Deck
from .exceptions import (
    CannotVoteForOwnCardError,
    DuplicateActionError,
    MulliganAlreadyUsedError,
    NotYourTurnError,
    WrongPhaseError,
)
from .player import Player


class Phase(Enum):
    HOST_CHOOSING = "host_choosing"
    OTHERS_CHOOSING = "others_choosing"
    VOTING = "voting"
    SCORING = "scoring"


@dataclass
class Round:
    host_name: str
    round_number: int = 1
    phase: Phase = Phase.HOST_CHOOSING
    prompt: str | None = None
    table: dict[str, Card] = field(default_factory=dict)
    votes: dict[str, str] = field(default_factory=dict)
    mulligans_used: set[str] = field(default_factory=set)
    scores: dict[str, int] = field(default_factory=dict)
    correct_voter_count: int = 0

    @property
    def is_scored(self) -> bool:
        return self.phase == Phase.SCORING

    def host_choice(self, host: Player, deck: Deck, card_id: str, prompt: str) -> None:
        if self.phase != Phase.HOST_CHOOSING:
            raise WrongPhaseError("choose the prompt card", self.phase.value)
        if host.name != self.host_name:
            raise NotYourTurnError(host.name)
        card = host.play_card(card_id, deck)
        self.table[host.name] = card
        self.prompt = prompt
        self.phase = Phase.OTHERS_CHOOSING

    def other_choice(self, player: Player, deck: Deck, card_id: str) -> None:
        if self.phase != Phase.OTHERS_CHOOSING:
            raise WrongPhaseError("play a card", self.phase.value)
        if player.name == self.host_name:
            raise NotYourTurnError(player.name)
        if player.name in self.table:
            raise DuplicateActionError(player.name, "play a card")
        self.table[player.name] = player.play_card(card_id, deck)

    def mulligan(self, player: Player, deck: Deck, card_id: str) -> None:
        if player.name in self.mulligans_used:
            raise MulliganAlreadyUsedError(player.name)
        is_host = player.name == self.host_name
        if is_host and self.phase != Phase.HOST_CHOOSING:
            raise WrongPhaseError("mulligan", self.phase.value)
        if not is_host and (self.phase != Phase.OTHERS_CHOOSING or player.name in self.table):
            raise WrongPhaseError("mulligan", self.phase.value)
        player.discard_card(card_id, deck)
        player.draw(deck)
        self.mulligans_used.add(player.name)

    def vote(self, player: Player, card_id: str) -> None:
        if self.phase != Phase.VOTING:
            raise WrongPhaseError("vote", self.phase.value)
        if player.name == self.host_name:
            raise NotYourTurnError(player.name)
        if player.name in self.votes:
            raise DuplicateActionError(player.name, "vote")
        own_card = self.table.get(player.name)
        if own_card is not None and own_card.id == card_id:
            raise CannotVoteForOwnCardError(player.name)
        self.votes[player.name] = card_id

    def all_humans_played(self, human_players: list[Player]) -> bool:
        return all(player.name in self.table for player in human_players)

    def all_humans_voted(self, human_players: list[Player]) -> bool:
        return all(
            player.name in self.votes for player in human_players if player.name != self.host_name
        )

    def resolve_cpu_choices(self, cpu_players: list[Player], deck: Deck) -> None:
        for cpu in cpu_players:
            card = random.choice(cpu.hand)
            self.table[cpu.name] = cpu.play_card(card.id, deck)
        self.phase = Phase.VOTING

    def resolve_cpu_votes(self, cpu_players: list[Player]) -> None:
        for cpu in cpu_players:
            candidates = [(name, card) for name, card in self.table.items() if name != cpu.name]
            raw_weights = [
                sum(1 for vote in self.votes.values() if vote == card.id) for _, card in candidates
            ]
            weights: list[int] | None = raw_weights if any(raw_weights) else None
            _, chosen_card = random.choices(candidates, weights=weights, k=1)[0]
            self.votes[cpu.name] = chosen_card.id

    def score(self, all_players: list[Player]) -> None:
        if self.phase != Phase.VOTING:
            raise WrongPhaseError("score the round", self.phase.value)
        deltas, correct_voter_count = self._score_deltas(all_players)
        for player in all_players:
            player.score += deltas[player.name]
        self.scores = deltas
        self.correct_voter_count = correct_voter_count
        self.phase = Phase.SCORING

    def _score_deltas(self, all_players: list[Player]) -> tuple[dict[str, int], int]:
        """Each player's point change this round, keyed by name, and how many
        non-host players voted for the host's card. CPUs never compete for
        score, so they're always 0.
        """
        deltas = {player.name: 0 for player in all_players}
        host_card_id = self.table[self.host_name].id
        others = [player for player in all_players if player.name != self.host_name]
        correct_voters = [
            player for player in others if self.votes.get(player.name) == host_card_id
        ]
        if len(correct_voters) in (0, len(others)):
            for player in others:
                if not player.is_cpu:
                    deltas[player.name] += 2
        else:
            deltas[self.host_name] += 3
            for player in correct_voters:
                if not player.is_cpu:
                    deltas[player.name] += 3
        for player in others:
            if player.is_cpu:
                continue
            own_card_id = self.table[player.name].id
            deltas[player.name] += sum(1 for vote in self.votes.values() if vote == own_card_id)
        return deltas, len(correct_voters)

    def to_dict(self) -> dict:
        return {
            "host_name": self.host_name,
            "round_number": self.round_number,
            "phase": self.phase.value,
            "prompt": self.prompt,
            "table": {name: card.id for name, card in self.table.items()},
            "votes": dict(self.votes),
            "mulligans_used": sorted(self.mulligans_used),
            "scores": dict(self.scores),
            "correct_voter_count": self.correct_voter_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Round:
        return cls(
            host_name=data["host_name"],
            round_number=data["round_number"],
            phase=Phase(data["phase"]),
            prompt=data["prompt"],
            table={name: Card(id=card_id) for name, card_id in data["table"].items()},
            votes=dict(data["votes"]),
            mulligans_used=set(data["mulligans_used"]),
            scores=dict(data["scores"]),
            correct_voter_count=data["correct_voter_count"],
        )
