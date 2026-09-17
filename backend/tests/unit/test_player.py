import pytest

from dixit.domain import Card, CardNotInHandError, Deck, Player


@pytest.fixture
def deck() -> Deck:
    return Deck(cards=[Card(id=f"{i}.jpg") for i in range(10)])


def test_draw_appends_a_card_to_the_hand(deck: Deck) -> None:
    player = Player(name="alice")
    player.draw(deck)
    assert len(player.hand) == 1


def test_play_card_removes_it_and_draws_a_replacement(deck: Deck) -> None:
    player = Player(name="alice", hand=[Card(id="x.jpg")])
    played = player.play_card("x.jpg", deck)
    assert played.id == "x.jpg"
    assert len(player.hand) == 1
    assert player.hand[0].id != "x.jpg"


def test_play_card_raises_for_a_card_not_in_hand(deck: Deck) -> None:
    player = Player(name="alice", hand=[])
    with pytest.raises(CardNotInHandError):
        player.play_card("missing.jpg", deck)


def test_discard_card_sends_it_to_the_deck(deck: Deck) -> None:
    player = Player(name="alice", hand=[Card(id="x.jpg")])
    player.discard_card("x.jpg", deck)
    assert player.hand == []
    assert deck.discard_pile == [Card(id="x.jpg")]


def test_round_trip_through_dict(deck: Deck) -> None:
    player = Player(name="alice", is_cpu=True, score=7, hand=[Card(id="x.jpg")])
    restored = Player.from_dict(player.to_dict())
    assert restored == player
