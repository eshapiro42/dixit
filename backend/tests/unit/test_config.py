import pytest

from dixit.config import Config


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    monkeypatch.setenv("SECRET_KEY", "secret")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("CARDS_DIR", "/cards")
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    return monkeypatch


def test_allowed_origins_default_to_none(env: pytest.MonkeyPatch) -> None:
    assert Config.from_env().allowed_origins == ()


def test_allowed_origins_are_split_and_trimmed(env: pytest.MonkeyPatch) -> None:
    env.setenv("ALLOWED_ORIGINS", " https://a.example , https://b.example,")

    assert Config.from_env().allowed_origins == ("https://a.example", "https://b.example")
