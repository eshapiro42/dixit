from dixit.api import views
from dixit.domain import Card, Phase, Player, Round


def _round(**overrides) -> Round:
    defaults = dict(
        host_name="host",
        phase=Phase.VOTING,
        prompt="a memory",
        table={
            "host": Card(id="h.jpg"),
            "a": Card(id="a.jpg"),
            "b": Card(id="b.jpg"),
        },
        votes={"a": "h.jpg"},
    )
    defaults.update(overrides)
    return Round(**defaults)


def test_visible_table_is_none_outside_voting() -> None:
    round_ = _round(phase=Phase.OTHERS_CHOOSING)
    assert views.visible_table(round_) is None


def test_visible_table_contains_every_card_id_and_no_names() -> None:
    round_ = _round()
    table = views.visible_table(round_)
    assert table is not None
    assert set(table) == {"h.jpg", "a.jpg", "b.jpg"}
    assert len(table) == 3


def test_round_outcome_is_fully_attributed() -> None:
    round_ = _round()
    outcome = views.round_outcome(round_)
    assert outcome == {
        "host": "host",
        "prompt": "a memory",
        "table": {"host": "h.jpg", "a": "a.jpg", "b": "b.jpg"},
        "votes": {"a": "h.jpg"},
    }


def test_has_played_true_once_on_the_table() -> None:
    round_ = _round()
    assert views.has_played(round_, Player(name="a")) is True
    assert views.has_played(round_, Player(name="carol")) is False


class TestMulliganAvailable:
    def test_host_before_choosing(self) -> None:
        round_ = _round(phase=Phase.HOST_CHOOSING, table={})
        assert views.mulligan_available(round_, Player(name="host")) is True

    def test_host_after_choosing(self) -> None:
        round_ = _round(phase=Phase.OTHERS_CHOOSING)
        assert views.mulligan_available(round_, Player(name="host")) is False

    def test_other_before_playing(self) -> None:
        round_ = _round(phase=Phase.OTHERS_CHOOSING, table={"host": Card(id="h.jpg")})
        assert views.mulligan_available(round_, Player(name="carol")) is True

    def test_other_after_playing(self) -> None:
        round_ = _round(phase=Phase.OTHERS_CHOOSING)
        assert views.mulligan_available(round_, Player(name="a")) is False

    def test_already_used(self) -> None:
        round_ = _round(phase=Phase.HOST_CHOOSING, table={}, mulligans_used={"host"})
        assert views.mulligan_available(round_, Player(name="host")) is False


def test_public_view_never_leaks_a_hand_or_votes(started_game) -> None:
    public = views.public_view(started_game)
    assert "hand" not in public
    assert "votes" not in public


def test_private_view_carries_only_the_viewers_hand(started_game) -> None:
    viewer = started_game.human_players[0]
    private = views.private_view(started_game, viewer)
    assert private["hand"] == [card.id for card in viewer.hand]
