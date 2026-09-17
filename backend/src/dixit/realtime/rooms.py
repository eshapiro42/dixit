def game_room(game_id: str) -> str:
    return f"game:{game_id}"


def player_room(game_id: str, player_name: str) -> str:
    return f"game:{game_id}:player:{_sanitize(player_name)}"


def _sanitize(name: str) -> str:
    return "".join(char if char.isalnum() or char in "-_" else "_" for char in name)
