import copy
import itertools
import os
import random


class State:
    HOST_CHOOSING = 0
    OTHERS_CHOOSING = 1
    VOTING = 2
    SCORING = 3


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
    def num_players(self):
        return len(self.players)

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

    def add_player(self, name):
        # If the game has already started, new players can't be added
        if self.started:
            print("Game {} has already started and new players cannot be added".format(self.id))
            return
        # Otherwise, create a new player object and add it to the game
        player = Player(name, self)
        self.players.append(player)
        print("Added player {} to game {}".format(name, self.id))
        # If the game has four or more players, it is playable
        if self.num_players >= 4:
            self.playable = True
            print("Game {} now has four players and is playable".format(self.id))
        return player

    def start(self):
        if self.playable:
            self.started = True
            random.shuffle(self.players)
            self.players_cycle = itertools.cycle(self.players)
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
            _ = yield
            # Other players choose their cards
            self.state = State.OTHERS_CHOOSING
            while len(self.current_round.table) < self.num_players:
                _ = yield
            # Other players vote
            self.state = State.VOTING
            while len(self.current_round.votes) < self.num_players - 1:
                _ = yield
            # Score the round
            self.state = State.SCORING
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

    def vote(self, player, player_vote):
        if self.game.state != State.VOTING or player == self.host:
            raise Exception("Action attempted during wrong game state")
        self.votes[player] = player_vote
        self.game.loop.send(None)

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
    def __init__(self, name, game):
        self.name = str(name)
        self.num = len(game.players)
        self.game = game
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
