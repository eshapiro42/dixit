from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Card:
    id: str


class CardLibrary:
    """The full set of card images available to be dealt, read once from disk."""

    def __init__(self, cards_dir: Path) -> None:
        self.directory = cards_dir
        self.cards = tuple(
            Card(id=path.name) for path in sorted(cards_dir.iterdir()) if path.is_file()
        )
        if not self.cards:
            raise ValueError(f"No card images found in {cards_dir}")
