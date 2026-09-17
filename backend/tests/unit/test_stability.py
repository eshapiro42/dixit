"""Full randomized playthroughs. Configuration and every move are randomized;
nothing is asserted beyond the game running to completion without raising. Any
illegal-state bug anywhere in the engine surfaces here as a crash.
"""

import random

import pytest

from dixit.domain import MIN_PLAYERS, CardLibrary, Game, Phase


@pytest.fixture(scope="module")
def large_card_library(tmp_path_factory) -> CardLibrary:
    directory = tmp_path_factory.mktemp("cards")
    for i in range(300):
        (directory / f"{i}.jpg").write_bytes(b"x")
    return CardLibrary(directory)


def _play_round(game: Game, rng: random.Random) -> None:
    round_ = game.current_round
    host = game.host

    if round_.phase == Phase.HOST_CHOOSING:
        card = rng.choice(host.hand)
        game.submit_host_choice(host, card.id, "a prompt")

    round_ = game.current_round
    if round_.phase == Phase.OTHERS_CHOOSING:
        others = [player for player in game.human_players if player.name != host.name]
        rng.shuffle(others)
        for player in others:
            if round_.phase != Phase.OTHERS_CHOOSING or player.name in round_.table:
                continue
            card = rng.choice(player.hand)
            game.submit_other_choice(player, card.id)

    round_ = game.current_round
    if round_.phase == Phase.VOTING:
        voters = [player for player in game.human_players if player.name != host.name]
        rng.shuffle(voters)
        for player in voters:
            if round_.phase != Phase.VOTING or player.name in round_.votes:
                continue
            own_card = round_.table.get(player.name)
            candidates = [card for card in round_.table.values() if card != own_card]
            card = rng.choice(candidates)
            game.submit_vote(player, card.id)


@pytest.mark.repeat(1000)
def test_stability(large_card_library: CardLibrary) -> None:
    """Play a full game with randomized player counts, CPU counts, and moves."""
    rng = random.Random()

    min_human_players = rng.randint(1, 3)
    num_humans = rng.randint(min_human_players, 6)
    num_cpus = rng.randint(0, 4)
    if num_humans + num_cpus < MIN_PLAYERS:
        num_cpus = MIN_PLAYERS - num_humans

    game = Game.new(
        "ABCD", large_card_library, creator_name="p0", min_human_players=min_human_players
    )
    for i in range(num_humans):
        game.add_player(f"p{i}")
    for i in range(num_cpus):
        game.add_player(f"cpu{i}", is_cpu=True)

    game.start()

    num_rounds = rng.randint(1, len(game.host_order) * 2)
    for _ in range(num_rounds):
        _play_round(game, rng)
        game.advance_round()
