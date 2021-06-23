from __future__ import annotations

from enum import Enum
import copy
import itertools
import os
import random


class State(Enum):
    HOST_CHOOSING = 0
    OTHERS_CHOOSING = 1
    CPUS_CHOOSING = 2
    VOTING = 3
    CPUS_VOTING = 4
    SCORING = 5

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class Game:
    def __init__(self, game_id):
        self.id = game_id
        self.players = []
        self.players_cycle = None
        self.current_round = None
        self.previous_round = None
        self.deck = Deck()
        self.playable = False
        self.started = False
        self.state = None
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
        # If people are still choosing cards, the table should still show the cards from last round
        if self.state < State.VOTING:
            if self.previous_round is not None:
                round_table = self.previous_round.table
        else:
            round_table = self.current_round.table
        # Put the table into a sendable format
        return {player.name: card for (player, card) in round_table.items()}

    @property
    def votes(self):
        return {player.name: vote for (player, vote) in self.current_round.votes.items()}

    @property
    def host(self):
        if self.current_round is not None:
            return self.current_round.host

    def add_player(self, name, cpu=False):
        # If the game has already started, new players can't be added
        if self.started:
            print(
                "Game {} has already started and new players cannot be added".format(self.id))
            return
        # Otherwise, create a new player object and add it to the game
        player = Player(name, self, cpu=cpu)
        self.players.append(player)
        print("Added player {} to game {}".format(name, self.id))
        # If the game has four or more players (at least two of them human), it is playable
        if self.num_players >= 4 and self.num_human_players >= 2:
            self.playable = True
            print("Game {} now has four players and is playable".format(self.id))
        return player

    def start(self):
        if self.playable:
            self.started = True
            human_players = self.human_players
            random.shuffle(human_players)
            self.players_cycle = itertools.cycle(human_players)
            self.loop = self.game_loop()
            next(self.loop)
            return "started"
        else:
            print("You need at least four players to play.")
            return

    def new_round(self):
        self.previous_round = self.current_round
        host = next(self.players_cycle)
        self.current_round = Round(self, host)

    def game_loop(self):
        while True:
            # Start a new round
            self.new_round()
            # Host chooses a card and prompt
            self.state = State.HOST_CHOOSING
            print(self.state.name)
            _ = yield
            # Other players choose their cards
            self.state = State.OTHERS_CHOOSING
            print(self.state.name)
            while len(self.current_round.table) < self.num_human_players:
                _ = yield
            self.state = State.CPUS_CHOOSING
            print(self.state.name)
            _ = yield
            # Other players vote
            self.state = State.VOTING
            print(self.state.name)
            while len(self.current_round.votes) < self.num_human_players - 1:
                _ = yield
            self.state = State.CPUS_VOTING
            print(self.state.name)
            _ = yield
            # Score the round
            self.state = State.SCORING
            print(self.state.name)
            self.current_round.score()
            # Wait until the round is ended
            _ = yield


class Round:
    def __init__(self, game, host):
        self.game = game
        self.host = host
        self.host_card = None
        self.host_prompt = None
        self.table = {}
        self.votes = {}

    def hostChoice(self, host_card, host_prompt):
        if self.game.state != State.HOST_CHOOSING:
            raise Exception("Action attempted during wrong game state")
        self.host_card = host_card
        self.host_prompt = host_prompt
        self.table[self.host] = self.host.play_card(host_card)
        self.game.loop.send(None)

    def otherChoice(self, player, player_card):
        if self.game.state != State.OTHERS_CHOOSING or player == self.host:
            raise Exception("Action attempted during wrong game state")
        self.table[player] = player.play_card(player_card)
        self.game.loop.send(None)

    def cpuChoice(self, player: Player):
        card = random.choice(player.hand)
        self.table[player] = player.play_card(card)

    def vote(self, player, player_vote):
        if self.game.state != State.VOTING or player == self.host:
            raise Exception("Action attempted during wrong game state")
        self.votes[player] = player_vote
        self.game.loop.send(None)

    def cpuVote(self, player: Player):
        table_cards = list(
            [card for card in self.table.values() if card != self.table[player]])
        vote_weights = [list(self.votes.values()).count(card)
                        for card in table_cards]
        vote = random.choices(population=table_cards,
                              weights=vote_weights, k=1)[0]
        self.votes[player] = vote

    def score(self):
        if self.game.state != State.SCORING:
            raise Exception("Action attempted during wrong game state")
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

    def end(self):
        if self.game.state != State.SCORING:
            raise Exception("Action attempted during wrong game state")
        self.game.loop.send(None)


class Player:
    def __init__(self, name, game, cpu=False):
        self.name = str(name)
        self.num = len(game.players)
        self.game = game
        self.is_cpu = cpu
        self.score = 0
        self.hand = []
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
        card_files = os.listdir("static/cards/")
        self.deck = card_files
        self.num_cards = len(self.deck)
        self.discard = []
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
