import random
import string
import sys
import threading
import time
from pusher import Pusher
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
)

from game import Game


app = Flask(__name__)
random.seed()
games = {}
pusher = Pusher(
    app_id='982239',
    key='aac926d8b7731623a59a',
    secret='199bad4a11c6eae764d1',
    cluster='us3'
)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/play')
def play(game_id=None):
    return render_template('game.html')


@app.route('/api/test')
def test():
    return 'success'


@app.route('/api/createGame', methods=['POST'])
def createGame():
    global games
    characters = string.ascii_uppercase + string.digits
    game_id = ''.join(random.choice(characters) for i in range(6))
    game = Game(game_id)
    games[game_id] = game
    player_name = request.form['player_name']
    joinGame(player_name, game_id)
    return play(game_id)


@app.route('/api/joinGame', methods=['POST'])
def joinGame(player_name=None, game_id=None):
    if player_name is None:
        player_name = request.form['player_name']
    if game_id is None:
        game_id = request.form['game_id']
    games[game_id].add_player(player_name)
    return play(game_id)


@app.route('/api/show-hand', methods=['POST'])
def show_hand(game_id=None, player_num=None):
    if game_id is None:
        game_id = request.form['game_id']
    if player_num is None:
        player_num = request.form['player_num']
    data = {
        'card1': '{}.jpg'.format(games[game_id].players[player_num].hand[0]),
        'card2': '{}.jpg'.format(games[game_id].players[player_num].hand[1]),
        'card3': '{}.jpg'.format(games[game_id].players[player_num].hand[2]),
        'card4': '{}.jpg'.format(games[game_id].players[player_num].hand[3]),
        'card5': '{}.jpg'.format(games[game_id].players[player_num].hand[4]),
        'message': 'Yo'
    }
    pusher.trigger('dixit', 'showHand', data)
    return jsonify(data)


app.run(debug=True)