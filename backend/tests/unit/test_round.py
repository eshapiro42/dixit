import pytest

from dixit.domain import (
    CannotVoteForOwnCardError,
    Card,
    Deck,
    DuplicateActionError,
    MulliganAlreadyUsedError,
    NotYourTurnError,
    Phase,
    Player,
    Round,
    WrongPhaseError,
)


@pytest.fixture
def deck() -> Deck:
    return Deck(cards=[Card(id=f"{i}.jpg") for i in range(30)])


@pytest.fixture
def host() -> Player:
    return Player(name="host", hand=[Card(id="host-card.jpg")])


@pytest.fixture
def other() -> Player:
    return Player(name="other", hand=[Card(id="other-card.jpg")])


@pytest.fixture
def round_(host: Player) -> Round:
    return Round(host_name=host.name)


class TestHostChoice:
    def test_moves_the_card_to_the_table_and_advances_the_phase(
        self, round_: Round, host: Player, deck: Deck
    ) -> None:
        round_.host_choice(host, deck, "host-card.jpg", "a prompt")
        assert round_.table[host.name].id == "host-card.jpg"
        assert round_.prompt == "a prompt"
        assert round_.phase == Phase.OTHERS_CHOOSING

    def test_raises_outside_the_host_choosing_phase(
        self, round_: Round, host: Player, deck: Deck
    ) -> None:
        round_.phase = Phase.VOTING
        with pytest.raises(WrongPhaseError):
            round_.host_choice(host, deck, "host-card.jpg", "a prompt")


class TestOtherChoice:
    def test_moves_the_card_to_the_table(
        self, round_: Round, other: Player, deck: Deck
    ) -> None:
        round_.phase = Phase.OTHERS_CHOOSING
        round_.other_choice(other, deck, "other-card.jpg")
        assert round_.table[other.name].id == "other-card.jpg"

    def test_raises_outside_the_others_choosing_phase(
        self, round_: Round, other: Player, deck: Deck
    ) -> None:
        with pytest.raises(WrongPhaseError):
            round_.other_choice(other, deck, "other-card.jpg")

    def test_raises_for_the_host(self, round_: Round, host: Player, deck: Deck) -> None:
        round_.phase = Phase.OTHERS_CHOOSING
        with pytest.raises(NotYourTurnError):
            round_.other_choice(host, deck, "host-card.jpg")

    def test_raises_for_a_second_submission(
        self, round_: Round, other: Player, deck: Deck
    ) -> None:
        round_.phase = Phase.OTHERS_CHOOSING
        round_.other_choice(other, deck, "other-card.jpg")
        with pytest.raises(DuplicateActionError):
            round_.other_choice(other, deck, other.hand[0].id)


class TestMulligan:
    def test_host_can_mulligan_before_choosing(
        self, round_: Round, host: Player, deck: Deck
    ) -> None:
        round_.mulligan(host, deck, "host-card.jpg")
        assert host.hand[0].id != "host-card.jpg"
        assert "host" in round_.mulligans_used

    def test_host_cannot_mulligan_after_choosing(
        self, round_: Round, host: Player, deck: Deck
    ) -> None:
        round_.host_choice(host, deck, "host-card.jpg", "a prompt")
        new_card = host.hand[0].id
        with pytest.raises(WrongPhaseError):
            round_.mulligan(host, deck, new_card)

    def test_other_player_can_mulligan_before_playing(
        self, round_: Round, other: Player, deck: Deck
    ) -> None:
        round_.phase = Phase.OTHERS_CHOOSING
        round_.mulligan(other, deck, "other-card.jpg")
        assert other.hand[0].id != "other-card.jpg"

    def test_other_player_cannot_mulligan_after_playing(
        self, round_: Round, other: Player, deck: Deck
    ) -> None:
        round_.phase = Phase.OTHERS_CHOOSING
        round_.other_choice(other, deck, "other-card.jpg")
        with pytest.raises(WrongPhaseError):
            round_.mulligan(other, deck, other.hand[0].id)

    def test_cannot_mulligan_twice_in_the_same_round(
        self, round_: Round, host: Player, deck: Deck
    ) -> None:
        round_.mulligan(host, deck, "host-card.jpg")
        with pytest.raises(MulliganAlreadyUsedError):
            round_.mulligan(host, deck, host.hand[0].id)

    def test_mulliganed_card_goes_to_the_discard_pile(
        self, round_: Round, host: Player, deck: Deck
    ) -> None:
        round_.mulligan(host, deck, "host-card.jpg")
        assert deck.discard_pile == [Card(id="host-card.jpg")]


class TestVote:
    @pytest.fixture(autouse=True)
    def voting_phase(self, round_: Round) -> None:
        round_.phase = Phase.VOTING
        round_.table = {"host": Card(id="host-card.jpg"), "other": Card(id="other-card.jpg")}

    def test_records_the_vote(self, round_: Round) -> None:
        round_.vote(Player(name="other"), "host-card.jpg")
        assert round_.votes["other"] == "host-card.jpg"

    def test_raises_outside_the_voting_phase(self, round_: Round) -> None:
        round_.phase = Phase.HOST_CHOOSING
        with pytest.raises(WrongPhaseError):
            round_.vote(Player(name="other"), "host-card.jpg")

    def test_raises_for_the_host(self, round_: Round) -> None:
        with pytest.raises(NotYourTurnError):
            round_.vote(Player(name="host"), "other-card.jpg")

    def test_raises_for_a_vote_for_ones_own_card(self, round_: Round) -> None:
        with pytest.raises(CannotVoteForOwnCardError):
            round_.vote(Player(name="other"), "other-card.jpg")

    def test_raises_for_a_second_vote(self, round_: Round) -> None:
        round_.vote(Player(name="other"), "host-card.jpg")
        with pytest.raises(DuplicateActionError):
            round_.vote(Player(name="other"), "host-card.jpg")


class TestResolveCpuVotes:
    def test_cpu_votes_for_a_card_on_the_table_that_is_not_its_own(self) -> None:
        round_ = Round(
            host_name="host",
            phase=Phase.VOTING,
            table={
                "host": Card(id="h.jpg"),
                "cpu": Card(id="c.jpg"),
                "other": Card(id="o.jpg"),
            },
        )
        cpu = Player(name="cpu", is_cpu=True)
        round_.resolve_cpu_votes([cpu])
        assert round_.votes["cpu"] in ("h.jpg", "o.jpg")

    def test_does_not_raise_when_no_human_has_voted_yet(self) -> None:
        round_ = Round(
            host_name="host",
            phase=Phase.VOTING,
            table={"host": Card(id="h.jpg"), "cpu": Card(id="c.jpg")},
        )
        cpu = Player(name="cpu", is_cpu=True)
        round_.resolve_cpu_votes([cpu])
        assert round_.votes["cpu"] == "h.jpg"


class TestScore:
    def _table_and_votes(self) -> Round:
        return Round(
            host_name="host",
            phase=Phase.VOTING,
            table={
                "host": Card(id="h.jpg"),
                "a": Card(id="a.jpg"),
                "b": Card(id="b.jpg"),
            },
        )

    def test_nobody_correct_awards_two_points_plus_a_bonus_per_vote_received(self) -> None:
        round_ = self._table_and_votes()
        round_.votes = {"a": "b.jpg", "b": "a.jpg"}
        players = [Player(name="host"), Player(name="a"), Player(name="b")]
        round_.score(players)
        scores = {p.name: p.score for p in players}
        # 2 base points each, plus 1 bonus point each for the vote their own card received
        assert scores == {"host": 0, "a": 3, "b": 3}
        assert round_.phase == Phase.SCORING

    def test_cpu_players_are_excluded_from_the_vote_received_bonus(self) -> None:
        round_ = self._table_and_votes()
        round_.votes = {"a": "b.jpg", "b": "a.jpg"}
        players = [Player(name="host"), Player(name="a", is_cpu=True), Player(name="b")]
        round_.score(players)
        assert players[1].score == 0

    def test_everyone_correct_awards_two_points_to_everyone_but_the_host(self) -> None:
        round_ = self._table_and_votes()
        round_.votes = {"a": "h.jpg", "b": "h.jpg"}
        players = [Player(name="host"), Player(name="a"), Player(name="b")]
        round_.score(players)
        scores = {p.name: p.score for p in players}
        assert scores == {"host": 0, "a": 2, "b": 2}

    def test_some_correct_awards_three_points_to_the_host_and_correct_voters(self) -> None:
        round_ = self._table_and_votes()
        round_.votes = {"a": "h.jpg", "b": "a.jpg"}
        players = [Player(name="host"), Player(name="a"), Player(name="b")]
        round_.score(players)
        scores = {p.name: p.score for p in players}
        # a voted correctly (+3) and also received b's vote for their own card (+1)
        assert scores == {"host": 3, "a": 4, "b": 0}

    def test_cpu_players_never_score(self) -> None:
        round_ = self._table_and_votes()
        round_.votes = {"a": "h.jpg", "b": "a.jpg"}
        players = [Player(name="host"), Player(name="a", is_cpu=True), Player(name="b")]
        round_.score(players)
        assert players[1].score == 0

    def test_raises_outside_the_voting_phase(self) -> None:
        round_ = self._table_and_votes()
        round_.phase = Phase.HOST_CHOOSING
        with pytest.raises(WrongPhaseError):
            round_.score([Player(name="host")])


def test_round_trip_through_dict() -> None:
    round_ = Round(
        host_name="host",
        phase=Phase.VOTING,
        prompt="a prompt",
        table={"host": Card(id="h.jpg")},
        votes={"a": "h.jpg"},
        mulligans_used={"a"},
    )
    restored = Round.from_dict(round_.to_dict())
    assert restored == round_
