from __future__ import annotations

from enum import Enum
from typing import Dict, Iterable, List, TYPE_CHECKING
from interactions import GameInteraction, PlayerInteraction, HumanInteraction, CPUInteraction
import copy
import itertools
import os
import random

if TYPE_CHECKING:
    from pusher import Pusher


class Game:
    def __init__(self, game_id: str, pusher: Pusher):
        self.id: str = game_id
        self.interactions: GameInteraction = GameInteraction(self, pusher)
        self.message_history: List[str] = []
        self.players: List[Player] = []
        self.creator: Player = None
        self.players_cycle: Iterable[Player] = None
        self.current_round: Round = None
        self.previous_round: Round = None
        self.deck: Deck = Deck()
        self.playable: bool = False
        self.started: bool = False
        print("Created game {}".format(self.id))

    @property
    def cpu_players(self):
        return [player for player in self.players if player.is_cpu]

    @property
    def human_players(self):
        return [player for player in self.players if not player.is_cpu]

    @property
    def num_players(self):
        return len(self.players)

    @property
    def num_cpu_players(self):
        return len(self.cpu_players)

    @property
    def num_human_players(self):
        return len(self.human_players)

    @property
    def table(self):
        # Put the table into a sendable format
        return {player.name: card for (player, card) in self.current_round.table.items()}

    @property
    def votes(self):
        return {player.name: vote for (player, vote) in self.current_round.votes.items()}

    @property
    def host(self):
        if self.current_round is not None:
            return self.current_round.host

    def add_player(self, name, cpu=False, creator=False):
        # If the game has already started, new players can't be added
        if self.started:
            print("Game {} has already started and new players cannot be added".format(self.id))
            return
        # Otherwise, create a new player object and add it to the game
        player = Player(name, self, cpu=cpu)
        self.players.append(player)
        if creator and self.creator is None:
            self.creator = player
        print("Added player {} to game {}".format(name, self.id))
        self.interactions.player_joined(player)
        # If the game has four or more players, it is playable
        if self.num_players >= 4:
            print("Game {} now has four players and is playable".format(self.id))
            self.playable = True
            self.interactions.game_playable()
        return player

    def start(self):
        if self.playable:
            self.started = True
            human_players = self.human_players
            random.shuffle(human_players)
            self.players_cycle = itertools.cycle(human_players)
            self.loop = self.game_loop()
            next(self.loop)
            self.interactions.game_started()
            return "started"
        else:
            print("You need at least four players to play.")
            return

    def new_round(self):
        self.previous_round = self.current_round
        host = next(self.players_cycle)
        self.current_round = Round(self, host)

    def game_loop(self):
        self.interactions.show_hands()
        while True:
            # Start a new round
            self.new_round()
            # Host chooses a card and prompt
            self.interactions.start_host_turn()
            _ = yield
            # Other players choose their cards
            self.interactions.start_other_turn()
            while len(self.current_round.table) < self.num_human_players:
                _ = yield
            for cpu_player in self.cpu_players:
                self.current_round.cpuChoice(cpu_player)
                self.interactions.send_message(f"{cpu_player.name} played a card.")
            # Other players vote
            self.interactions.show_table()
            self.interactions.start_voting()
            while len(self.current_round.votes) < self.num_human_players - 1:
                _ = yield
            for cpu_player in self.cpu_players:
                self.current_round.cpuVote(cpu_player)
                self.interactions.send_message(f"{cpu_player.name} voted.")
            # Score the round
            self.current_round.score()
            self.interactions.send_outcomes()
            self.interactions.send_score_update()


class Round:
    def __init__(self, game, host):
        self.game: Game = game
        self.host: Player = host
        self.host_card: str = None
        self.host_prompt: str = None
        self.table: Dict[Player, str] = {}
        self.votes: Dict[Player, str] = {}
        self.cpu_vote_weights: List[int] = None

    def hostChoice(self, host_card, host_prompt):
        self.host_card = host_card
        self.host_prompt = host_prompt
        self.table[self.host] = self.host.play_card(host_card)
        self.game.loop.send(None)

    def otherChoice(self, player, player_card):
        self.table[player] = player.play_card(player_card)
        self.game.loop.send(None)

    def cpuChoice(self, player: Player):
        card = random.choice(player.hand)
        self.table[player] = player.play_card(card)

    def vote(self, player, player_vote):
        self.votes[player] = player_vote
        self.game.loop.send(None)

    def cpuVote(self, player: Player):
        table_cards = list(self.table.values())
        if self.cpu_vote_weights is None:
            self.cpu_vote_weights = [list(self.votes.values()).count(card) for card in table_cards]
        vote = random.choices(population=table_cards, weights=self.cpu_vote_weights, k=1)[0]
        self.votes[player] = vote

    def score(self):
        other_players = copy.copy(self.game.players)
        other_players.remove(self.host)
        num_correct_votes = list(self.votes.values()).count(self.host_card)
        # If nobody or everybody finds the correct card, the host scores 0 and other players scores 2
        if num_correct_votes in [0, self.game.num_players - 1]:
            for player in other_players:
                player.score += 2
        # Otherwise, the host and whoever found the correct answer score 3
        else:
            self.host.score += 3
            for player in other_players:
                if self.votes[player] == self.host_card:
                    player.score += 3
        # Players score 1 point for every vote for their own card
        for player in other_players:
            num_votes = list(self.votes.values()).count(self.table[player])
            player.score += num_votes


class Player:
    def __init__(self, name, game, cpu=False):
        self.name: str = str(name)
        self.num: int = len(game.players)
        self.game: Game = game
        self.is_cpu: bool = cpu
        self.score: int = 0
        self.hand: List[str] = []
        if cpu:
            self.interactions: PlayerInteraction = CPUInteraction(self)
        else:
            self.interactions: PlayerInteraction = HumanInteraction(self)
        for _ in range(6):
            self.draw_card()

    def __repr__(self):
        return self.name

    def draw_card(self):
        self.hand.append(self.game.deck.draw_card())
        print(self.name, self.hand)

    def play_card(self, card):
        self.hand.remove(card)
        self.draw_card()
        return card

    def discard_card(self, card):
        self.hand.remove(card)
        self.game.deck.discard_card(card)


class Deck:
    def __init__(self):
        self.deck: List[str] = os.listdir("static/cards/")
        self.num_cards: int = len(self.deck)
        self.discard: List[str] = []
        random.shuffle(self.deck)

    def draw_card(self):
        try:
            return self.deck.pop()
        except IndexError:
            self.shuffle_deck()
            return self.deck.pop()

    def discard_card(self, card):
        self.discard.append(card)

    def shuffle_deck(self):
        self.deck += self.discard
        random.shuffle(self.deck)
