from __future__ import annotations

from abc import abstractmethod
from enum import Enum, auto
import random
from typing import Dict, Optional, TYPE_CHECKING

import string

if TYPE_CHECKING:
    from game import Game, Player
    from pusher import Pusher


class GameEvent(Enum):
    PLAYER_JOINED = auto()
    GAME_PLAYABLE = auto()


class PlayerEvent(Enum):
    HOST_TURN = auto()
    OTHER_TURN = auto()
    START_VOTING = auto()


class GameInteraction:
    def __init__(self, game: Game, pusher: Pusher):
        self.game: Game = game
        self.pusher: Pusher = pusher
        self.pusher_channel: str = f"dixit-{game.id}"

    def trigger(self, event: str, data: Optional[Dict]):
        self.pusher.trigger(self.pusher_channel, event, data)

    def send_message(self, message, bold=False):
        if bold:
            message = f"<b>{message}</b>"
        self.game.message_history.append(message)
        self.trigger("gameMessage", {"gameMessage": message})

    def player_joined(self, player: Player):
        self.trigger("playerJoined", {"playerName": player.name})

    def game_playable(self):
        self.trigger("gamePlayable", None)

    def game_started(self):
        self.trigger(
            "started",
            {
                "started": True,
                "num_players": self.game.num_players,
            },
        )

    def show_hands(self):
        for player in self.game.players:
            player.interactions.show_hand()

    def start_host_turn(self):
        host_name: str = self.game.host.name
        self.send_message(f"It is {host_name}'s turn to choose a card and give a prompt.")
        self.trigger("startHostTurn", {"host": host_name})

    def send_host_prompt(self, prompt):
        self.trigger("hostPrompt", {"hostPrompt": prompt})

    def start_other_turn(self):
        host_name: str = self.game.host.name
        self.send_message(f"Other players, choose a card to match the prompt.")
        self.trigger("startOtherTurn", {"host": host_name})

    def start_voting(self):
        host_name: str = self.game.host.name
        self.send_message(f"Other players, vote for whichever card you think matches the prompt.")
        self.trigger("startVoting", {"host": host_name})

    def show_table(self):
        table_list = list(self.game.table.values())
        random.shuffle(table_list)
        self.trigger("showTable", table_list)

    def send_outcomes(self):
        data = {
            "cardPlayers": self.game.table,
            "cardVoters": self.game.votes,
            "host": self.game.host.name,
        }
        self.trigger("sendOutcomes", data)

    def send_score_update(self):
        score_html = "<tr>"
        for player_object in self.game.players:
            score_html += "\n<td> {} </td>".format(player_object.name)
        score_html += "\n</tr>\n<tr>"
        for player_object in self.game.players:
            score_html += "\n<td> {} </td>".format(player_object.score)
        score_html += "\n</tr>"
        data = {
            "scores": score_html,
        }
        self.trigger("scoreUpdate", data)


class PlayerInteraction:
    def __init__(self, player: Player):
        self.player: Player = player
        self.game: Game = player.game
        self.pusher: Pusher = self.game.interactions.pusher
        self._pusher_channel: str = None

    @property
    def pusher_channel(self):
        if self._pusher_channel is None:
            allowed_characters = string.ascii_letters + string.digits + "_-=@,.;"
            channel_name = self.player.name
            for character in self.player.name:
                if character not in allowed_characters:
                    channel_name = channel_name.replace(character, "_")
            self._pusher_channel = "dixit-{}-{}".format(channel_name, self.game.id)
        return self._pusher_channel

    def trigger(self, event: str, data: Optional[Dict]):
        self.pusher.trigger(self.pusher_channel, event, data)

    @abstractmethod
    def send_message_history(self):
        pass

    @abstractmethod
    def show_hand(self):
        pass

    @abstractmethod
    def send_event(self, event: PlayerEvent):
        pass


class HumanInteraction(PlayerInteraction):
    def send_message_history(self):
        """
        Send all past messages to a player.

        Currently used for when a new player joins to see existing message history.
        Can be repurposed for player rejoining in the future.
        """
        for message in self.game.message_history:
            self.trigger("gameMessage", {"gameMessage": message})

    def show_hand(self):
        self.trigger("showHand", self.player.hand)


class CPUInteraction(PlayerInteraction):
    def send_message_history(self):
        pass

    def show_hand(self):
        pass
