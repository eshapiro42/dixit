import threading

import fakeredis
import pytest

from dixit.domain import CardLibrary, Game, GameNotFoundError
from dixit.store import GameStore, InMemoryGameStore, RedisGameStore


@pytest.fixture(params=["memory", "redis"])
def store(request: pytest.FixtureRequest) -> GameStore:
    if request.param == "memory":
        return InMemoryGameStore()
    return RedisGameStore(fakeredis.FakeRedis())


def test_a_created_game_exists(store: GameStore, game: Game) -> None:
    assert not store.exists(game.id)
    store.create(game)
    assert store.exists(game.id)


def test_transaction_yields_an_equivalent_game(store: GameStore, game: Game) -> None:
    store.create(game)
    with store.transaction(game.id) as loaded:
        assert loaded.id == game.id
        assert len(loaded.players) == len(game.players)


def test_transaction_persists_mutations(store: GameStore, game: Game) -> None:
    store.create(game)
    with store.transaction(game.id) as loaded:
        loaded.add_player("alice")
    with store.transaction(game.id) as reloaded:
        assert reloaded.has_player("alice")


def test_transaction_does_not_persist_on_exception(store: GameStore, game: Game) -> None:
    store.create(game)
    with pytest.raises(RuntimeError):
        with store.transaction(game.id) as loaded:
            loaded.add_player("alice")
            raise RuntimeError("boom")
    with store.transaction(game.id) as reloaded:
        assert not reloaded.has_player("alice")


def test_transaction_raises_for_an_unknown_game(store: GameStore) -> None:
    with pytest.raises(GameNotFoundError):
        with store.transaction("NOPE"):
            pass


def test_transaction_serializes_concurrent_mutations(store: GameStore, tmp_path) -> None:
    for i in range(300):
        (tmp_path / f"{i}.jpg").write_bytes(b"x")
    game = Game.new("RACE", CardLibrary(tmp_path), creator_name="alice")
    store.create(game)
    errors: list[Exception] = []

    def add_players(prefix: str) -> None:
        try:
            for i in range(20):
                with store.transaction("RACE") as loaded:
                    loaded.add_player(f"{prefix}{i}")
        except Exception as exc:  # pragma: no cover - surfaced via errors list
            errors.append(exc)

    threads = [threading.Thread(target=add_players, args=(prefix,)) for prefix in ("a", "b")]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors
    with store.transaction("RACE") as final:
        assert final.num_players == 40


def test_redis_transaction_does_not_resurrect_a_key_deleted_mid_transaction(
    game: Game,
) -> None:
    client = fakeredis.FakeRedis()
    store = RedisGameStore(client)
    store.create(game)

    with pytest.raises(GameNotFoundError):
        with store.transaction(game.id) as loaded:
            loaded.add_player("alice")
            client.delete(f"dixit:game:{game.id}")

    assert not store.exists(game.id)
