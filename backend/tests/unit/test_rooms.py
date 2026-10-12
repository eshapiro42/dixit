from dixit.realtime import game_room, player_room


def test_game_room_is_scoped_to_the_game_id() -> None:
    assert game_room("ABCD") != game_room("WXYZ")


def test_player_room_is_scoped_to_both_game_and_player() -> None:
    assert player_room("ABCD", "alice") != player_room("ABCD", "bob")
    assert player_room("ABCD", "alice") != player_room("WXYZ", "alice")


def test_player_room_does_not_collide_for_names_that_sanitize_the_same_way() -> None:
    # These would previously map to the same room once non-alphanumeric
    # characters were replaced with '_', leaking one player's hand to the other.
    assert player_room("ABCD", "Zoe!") != player_room("ABCD", "Zoe@")
    assert player_room("ABCD", "a b") != player_room("ABCD", "a_b")


def test_player_room_is_deterministic() -> None:
    assert player_room("ABCD", "alice") == player_room("ABCD", "alice")
