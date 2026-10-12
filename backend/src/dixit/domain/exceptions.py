class DixitError(Exception):
    """Base class for errors a client request can trigger."""


class DeckExhaustedError(DixitError):
    def __init__(self) -> None:
        super().__init__("No cards remain in the deck or the discard pile.")


class GameNotFoundError(DixitError):
    def __init__(self, game_id: str) -> None:
        super().__init__(f"Game {game_id} was not found.")
        self.game_id = game_id


class PlayerNotFoundError(DixitError):
    def __init__(self, player_name: str, game_id: str) -> None:
        super().__init__(f"Player {player_name} was not found in game {game_id}.")
        self.player_name = player_name
        self.game_id = game_id


class GameAlreadyStartedError(DixitError):
    def __init__(self, game_id: str) -> None:
        super().__init__(f"Game {game_id} has already started.")
        self.game_id = game_id


class GameNotStartedError(DixitError):
    def __init__(self, game_id: str) -> None:
        super().__init__(f"Game {game_id} has not started yet.")
        self.game_id = game_id


class DuplicatePlayerNameError(DixitError):
    def __init__(self, player_name: str) -> None:
        super().__init__(f"{player_name} is already in this game.")
        self.player_name = player_name


class NotEnoughPlayersError(DixitError):
    def __init__(self, min_players: int, min_human_players: int) -> None:
        super().__init__(
            f"A game needs at least {min_players} players, {min_human_players} of them human."
        )


class WrongPhaseError(DixitError):
    def __init__(self, action: str, phase: str) -> None:
        super().__init__(f"Cannot {action} during the {phase} phase.")
        self.action = action
        self.phase = phase


class NotYourTurnError(DixitError):
    def __init__(self, player_name: str) -> None:
        super().__init__(f"It is not {player_name}'s turn.")
        self.player_name = player_name


class CardNotInHandError(DixitError):
    def __init__(self, player_name: str, card_id: str) -> None:
        super().__init__(f"{player_name} does not hold card {card_id}.")
        self.player_name = player_name
        self.card_id = card_id


class MulliganAlreadyUsedError(DixitError):
    def __init__(self, player_name: str) -> None:
        super().__init__(f"{player_name} has already used their mulligan this round.")
        self.player_name = player_name


class DuplicateActionError(DixitError):
    def __init__(self, player_name: str, action: str) -> None:
        super().__init__(f"{player_name} cannot {action} twice in the same round.")
        self.player_name = player_name
        self.action = action


class CannotVoteForOwnCardError(DixitError):
    def __init__(self, player_name: str) -> None:
        super().__init__(f"{player_name} cannot vote for their own card.")
        self.player_name = player_name
