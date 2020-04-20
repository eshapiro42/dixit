import itertools
import os
import random

class Game:
    def __init__(self, game_id):
        self.id = game_id
        self.players = {}
        self.players_cycle = None
        self.current_host = None
        self.host_card = None
        self.host_prompt = None
        self.num_players = 0
        self.deck = Deck()
        self.table = {}
        self.votes = {}
        self.playable = False
        self.started = False
        print('Created game {}'.format(self.id))

    def add_player(self, name):
        # If the game has already started, new players can't be added
        if self.started:
            print('Game {} has already started and new players cannot be added'.format(self.id))
            return None
        # Otherwise, create a new player object and add it to the game
        player = Player(name, self)
        self.players[name] = player
        print('Added player {} to game {}'.format(name, self.id))
        # If the game has four or more players, it is playable
        self.num_players += 1
        # TODO: UNCOMMENT THIS
        # if self.num_players >= 4:
        #     self.playable = True
        #     print('Game {} now has four players and is playable'.format(self.id))
        self.playable = True
        return player
        
    def start_game(self):
        if self.playable:
            self.started = True
            players_list = list(self.players.values())
            random.shuffle(players_list)
            self.players_cycle = itertools.cycle(players_list)
            return 'started'
        else:
            print("You need at least four players to play.")
            return None

    def new_round(self):
        self.host_card = None
        self.host_prompt = None
        self.table = {}
        self.votes = {}
        self.current_host = next(self.players_cycle)


class Player:
    def __init__(self, name, game):
        self.name = name
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
        card_files = os.listdir('static/cards/')
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