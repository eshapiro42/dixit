import json

import pytest

from dixit.domain import (
    CardLibrary,
    DuplicateActionError,
    Game,
    GameAlreadyStartedError,
    NotEnoughPlayersError,
    Phase,
    WrongPhaseError,
)


def test_add_player_deals_a_full_hand(game: Game) -> None:
    player = game.add_player("alice")
    assert len(player.hand) == 6


def test_add_player_raises_once_the_game_has_started(started_game: Game) -> None:
    with pytest.raises(GameAlreadyStartedError):
        started_game.add_player("dave")


@pytest.mark.parametrize(
    ("humans", "cpus", "expected"),
    [
        (["a", "b", "c"], [], False),
        (["a", "b", "c"], ["cpu"], True),
        (["a", "b"], ["cpu1", "cpu2"], False),
        (["a", "b", "c", "d"], [], True),
    ],
)
def test_playable_requires_four_players_with_three_human(
    game: Game, humans: list[str], cpus: list[str], expected: bool
) -> None:
    for name in humans:
        game.add_player(name)
    for name in cpus:
        game.add_player(name, is_cpu=True)
    assert game.playable is expected


def test_start_raises_when_not_playable(game: Game) -> None:
    game.add_player("alice")
    game.add_player("bob")
    with pytest.raises(NotEnoughPlayersError):
        game.start()


def test_min_human_players_is_configurable(card_library: CardLibrary) -> None:
    game = Game.new("ABCD", card_library, creator_name="alice", min_human_players=1)
    game.add_player("alice")
    for i in range(3):
        game.add_player(f"CPU-{i}", is_cpu=True)
    assert game.playable is True
    game.start()
    assert game.started is True


def test_start_only_selects_a_human_host(game: Game) -> None:
    for name in ("alice", "bob", "carol"):
        game.add_player(name)
    game.add_player("CPU-0", is_cpu=True)
    game.start()
    assert set(game.host_order) == {"alice", "bob", "carol"}
    assert game.host.name in game.host_order


def test_host_rotates_across_rounds(started_game: Game) -> None:
    seen_hosts = [started_game.host.name]
    for _ in range(len(started_game.host_order) * 2):
        started_game.current_round.phase = Phase.SCORING
        started_game.advance_round()
        seen_hosts.append(started_game.host.name)
    # every human takes a turn before anyone repeats
    first_cycle = seen_hosts[: len(started_game.host_order)]
    assert set(first_cycle) == set(started_game.host_order)


def test_advance_round_raises_before_scoring(started_game: Game) -> None:
    with pytest.raises(WrongPhaseError):
        started_game.advance_round()


def _play_full_round(game: Game) -> None:
    host = game.host
    game.submit_host_choice(host, host.hand[0].id, "a prompt")
    for player in game.human_players:
        if player.name == host.name:
            continue
        game.submit_other_choice(player, game.player(player.name).hand[0].id)
    for player in game.human_players:
        if player.name == host.name:
            continue
        candidates = [
            card for name, card in game.current_round.table.items() if name != player.name
        ]
        game.submit_vote(player, candidates[0].id)


def test_a_full_round_scores_and_can_advance(started_game: Game) -> None:
    _play_full_round(started_game)
    assert started_game.current_round.is_scored
    assert started_game.current_round.votes.get("CPU-0") is not None
    started_game.advance_round()
    assert started_game.current_round.phase == Phase.HOST_CHOOSING


def test_duplicate_choice_from_the_same_player_raises(started_game: Game) -> None:
    host = started_game.host
    started_game.submit_host_choice(host, host.hand[0].id, "a prompt")
    other = next(p for p in started_game.human_players if p.name != host.name)
    started_game.submit_other_choice(other, other.hand[0].id)
    with pytest.raises(DuplicateActionError):
        started_game.submit_other_choice(started_game.player(other.name), other.hand[0].id)


def test_round_trip_through_dict(started_game: Game) -> None:
    _play_full_round(started_game)
    restored = Game.from_dict(json.loads(json.dumps(started_game.to_dict())))
    assert restored.to_dict() == started_game.to_dict()


def test_card_library_rejects_an_empty_directory(tmp_path) -> None:
    with pytest.raises(ValueError):
        CardLibrary(tmp_path)
