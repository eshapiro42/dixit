from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .domain import MIN_HUMAN_PLAYERS


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Config:
    secret_key: str
    redis_url: str
    cards_dir: Path
    min_human_players: int = MIN_HUMAN_PLAYERS
    allowed_origins: tuple[str, ...] = ()

    @classmethod
    def from_env(cls) -> Config:
        min_human_players = int(os.environ.get("MIN_HUMAN_PLAYERS", MIN_HUMAN_PLAYERS))
        if min_human_players < 1:
            raise ConfigError("MIN_HUMAN_PLAYERS must be at least 1: a round always needs a host.")
        return cls(
            secret_key=_require("SECRET_KEY"),
            redis_url=_require("REDIS_URL"),
            cards_dir=Path(_require("CARDS_DIR")),
            min_human_players=min_human_players,
            allowed_origins=tuple(
                origin.strip()
                for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",")
                if origin.strip()
            ),
        )


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ConfigError(f"{name} must be set in the environment.")
    return value
