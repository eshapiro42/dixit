from __future__ import annotations

import random
from dataclasses import dataclass, field

from .card import Card, CardLibrary
from .exceptions import DeckExhaustedError


@dataclass
class Deck:
    cards: list[Card]
    discard_pile: list[Card] = field(default_factory=list)

    @classmethod
    def shuffled(cls, library: CardLibrary) -> Deck:
        cards = list(library.cards)
        random.shuffle(cards)
        return cls(cards=cards)

    def draw(self) -> Card:
        if not self.cards:
            self._reshuffle_discard()
        if not self.cards:
            raise DeckExhaustedError()
        return self.cards.pop()

    def discard(self, card: Card) -> None:
        self.discard_pile.append(card)

    def _reshuffle_discard(self) -> None:
        self.cards, self.discard_pile = self.discard_pile, []
        random.shuffle(self.cards)

    def to_dict(self) -> dict:
        return {
            "cards": [card.id for card in self.cards],
            "discard_pile": [card.id for card in self.discard_pile],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Deck:
        return cls(
            cards=[Card(id=card_id) for card_id in data["cards"]],
            discard_pile=[Card(id=card_id) for card_id in data["discard_pile"]],
        )
