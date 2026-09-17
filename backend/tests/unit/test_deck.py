import pytest

from dixit.domain import Card, CardLibrary, Deck, DeckExhaustedError


def test_shuffled_deck_contains_every_card(card_library: CardLibrary) -> None:
    deck = Deck.shuffled(card_library)
    assert {card.id for card in deck.cards} == {card.id for card in card_library.cards}


def test_draw_removes_the_card_from_the_deck(card_library: CardLibrary) -> None:
    deck = Deck.shuffled(card_library)
    remaining = len(deck.cards)
    card = deck.draw()
    assert card not in deck.cards
    assert len(deck.cards) == remaining - 1


def test_draw_reshuffles_the_discard_pile_once_the_deck_is_empty() -> None:
    deck = Deck(cards=[], discard_pile=[Card(id="a"), Card(id="b")])
    card = deck.draw()
    assert card.id in ("a", "b")
    assert deck.discard_pile == []
    assert len(deck.cards) == 1


def test_draw_raises_once_both_piles_are_empty() -> None:
    deck = Deck(cards=[], discard_pile=[])
    with pytest.raises(DeckExhaustedError):
        deck.draw()


def test_discard_moves_a_card_to_the_discard_pile() -> None:
    deck = Deck(cards=[])
    card = Card(id="a")
    deck.discard(card)
    assert deck.discard_pile == [card]


def test_round_trip_through_dict(card_library: CardLibrary) -> None:
    deck = Deck.shuffled(card_library)
    deck.discard(deck.draw())
    restored = Deck.from_dict(deck.to_dict())
    assert restored.cards == deck.cards
    assert restored.discard_pile == deck.discard_pile
