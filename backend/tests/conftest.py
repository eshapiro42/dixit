from pathlib import Path

import pytest

from dixit.domain import CardLibrary, Game


@pytest.fixture
def card_library(tmp_path: Path) -> CardLibrary:
    for i in range(60):
        (tmp_path / f"{i}.jpg").write_bytes(b"x")
    return CardLibrary(tmp_path)


@pytest.fixture
def game(card_library: CardLibrary) -> Game:
    return Game.new("ABCD", card_library, creator_name="alice")


@pytest.fixture
def started_game(game: Game) -> Game:
    for name in ("alice", "bob", "carol"):
        game.add_player(name)
    game.add_player("CPU-0", is_cpu=True)
    game.start()
    return game
