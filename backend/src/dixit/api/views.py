from __future__ import annotations

import random

from dixit.domain import Game, Phase, Player, Round


def player_summary(player: Player) -> dict:
    return {"name": player.name, "score": player.score, "is_cpu": player.is_cpu}


def round_outcome(round_: Round) -> dict:
    """The full, attributed result of a finished round: safe to reveal once scored."""
    return {
        "host": round_.host_name,
        "prompt": round_.prompt,
        "table": {name: card.id for name, card in round_.table.items()},
        "votes": dict(round_.votes),
    }


def visible_table(round_: Round) -> list[str] | None:
    """Cards on the table for the current round, shuffled and unattributed, so a
    voter sees only what Dixit intends them to: which cards, not whose.
    """
    if round_.phase != Phase.VOTING:
        return None
    card_ids = [card.id for card in round_.table.values()]
    random.shuffle(card_ids)
    return card_ids


def mulligan_available(round_: Round, player: Player) -> bool:
    if player.name in round_.mulligans_used:
        return False
    if player.name == round_.host_name:
        return round_.phase == Phase.HOST_CHOOSING
    return round_.phase == Phase.OTHERS_CHOOSING and player.name not in round_.table


def has_played(round_: Round, player: Player) -> bool:
    """Whether this player has already submitted a card this round. Hand size
    can't tell you this: a play immediately draws a replacement.
    """
    return player.name in round_.table


def has_voted(round_: Round, player: Player) -> bool:
    return player.name in round_.votes


def public_view(game: Game) -> dict:
    """The shared view of a game: the same for every player, broadcast as `state`."""
    current = game.current_round
    return {
        "game_id": game.id,
        "started": game.started,
        "playable": game.playable,
        "players": [player_summary(p) for p in game.players],
        "phase": current.phase.value if current else None,
        "host": current.host_name if current else None,
        "prompt": current.prompt if current else None,
        "table": visible_table(current) if current else None,
    }


def private_view(game: Game, player: Player) -> dict:
    """What only this player should see: their own hand, sent as `you`."""
    current = game.current_round
    return {
        "player_name": player.name,
        "is_creator": player.name == game.creator_name,
        "hand": [card.id for card in player.hand],
        "mulligan_available": mulligan_available(current, player) if current else False,
        "has_played": has_played(current, player) if current else False,
        "has_voted": has_voted(current, player) if current else False,
    }


def session_view(game: Game, player_name: str) -> dict:
    """Everything the given player is entitled to see, for a one-shot fetch."""
    player = game.player(player_name)
    return {
        **public_view(game),
        **private_view(game, player),
        "previous_round_outcome": (
            round_outcome(game.previous_round) if game.previous_round else None
        ),
    }
