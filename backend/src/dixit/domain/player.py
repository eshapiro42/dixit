from __future__ import annotations

from dataclasses import dataclass, field

from .card import Card
from .deck import Deck
from .exceptions import CardNotInHandError

HAND_SIZE = 6


@dataclass
class Player:
    name: str
    is_cpu: bool = False
    score: int = 0
    hand: list[Card] = field(default_factory=list)

    def draw(self, deck: Deck) -> None:
        self.hand.append(deck.draw())

    def play_card(self, card_id: str, deck: Deck) -> Card:
        card = self._remove_from_hand(card_id)
        self.draw(deck)
        return card

    def discard_card(self, card_id: str, deck: Deck) -> Card:
        card = self._remove_from_hand(card_id)
        deck.discard(card)
        return card

    def _remove_from_hand(self, card_id: str) -> Card:
        for card in self.hand:
            if card.id == card_id:
                self.hand.remove(card)
                return card
        raise CardNotInHandError(self.name, card_id)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "is_cpu": self.is_cpu,
            "score": self.score,
            "hand": [card.id for card in self.hand],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Player:
        return cls(
            name=data["name"],
            is_cpu=data["is_cpu"],
            score=data["score"],
            hand=[Card(id=card_id) for card_id in data["hand"]],
        )
