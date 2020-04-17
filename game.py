import random

class Game:
    def __init__(self, game_id):
        self.id = game_id
        self.players = []
        self.deck = Deck()
        self.playable = False
        self.started = False
        print('Created game {}'.format(self.id))

    def add_player(self, name):
        self.players.append(Player(name, self))
        if len(self.players) >= 4:
            self.playable = True
        print('Added player {} to game {}'.format(name, self.id))
        
    def start_game(self):
        if self.playable:
            self.started = True
            self.round_loop()
        else:
            print("You need at least four players to play.")

    def round_loop(self):
        while all([player.score < 30 for player in self.players]):
            for num in range(len(self.players)):
                host_player = self.players[num]
                other_players = self.players[:num] + self.players[num + 1:]
                round = Round(self, host_player, other_players)
                round.start()


class Round:
    def __init__(self, game, host_player, other_players):
        self.game = game
        self.host_player = host_player
        self.other_players = other_players

    def start(self):
        print('Host: {}'.format(self.host_player))
        # host player chooses a card and creates a prompt
        # other players receive the prompt and choose a card 
        # round gets scored
        for player in self.game.players:
            player.score += 5
        # all players draw a card
        for player in self.game.players:
            player.draw_card()
            player.discard_card(player.hand[0])


class Player:
    def __init__(self, name, game):
        self.name = name
        self.game = game
        self.score = 0
        self.hand = []
        for pick in range(5):
            self.draw_card()
        print(self.name, self.hand)

    def __repr__(self):
        return self.name

    def draw_card(self):
        self.hand.append(self.game.deck.draw_card())
        print(self.name, self.hand)

    def discard_card(self, card):
        self.hand.remove(card)
        self.game.deck.discard_card(card)


class Deck:
    def __init__(self):
        self.num_cards = 108
        self.deck = list(range(108))
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