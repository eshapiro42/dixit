import hashlib


def game_room(game_id: str) -> str:
    return f"game:{game_id}"


def player_room(game_id: str, player_name: str) -> str:
    # A room name built from a lossily-sanitized player name would let two
    # different names collide onto the same private room. Hashing the exact
    # name keeps the room private-per-player with no restriction on the name.
    digest = hashlib.sha256(player_name.encode()).hexdigest()[:16]
    return f"game:{game_id}:player:{digest}"
