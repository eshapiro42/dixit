import os
import random
import string
import sys
import threading
import time
from pusher import Pusher
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from game import Game


app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.urandom(24),
)
random.seed()
games = {}
players = {}
messages = {}
pusher = Pusher(
    app_id='982239',
    key='aac926d8b7731623a59a',
    secret='199bad4a11c6eae764d1',
    cluster='us3'
)


@app.route('/')
def index():
    if 'player_name' in session:
        players.pop(session['player_name'], None)
    session.clear()
    return render_template('index.html')


@app.route('/play', methods=['GET', 'POST'])
def play():
    print('PLAY Session data: {}'.format(session))
    data = {
        'player_name': session['player_name'],
        'game_id': session['game_id'],
        'host': session['host'],
        'started': games[session['game_id']].started,
    }
    return render_template('play.html', data=data)


@app.route('/api/test')
def test():
    return 'success'


@app.route('/api/createGame', methods=['POST'])
def createGame():
    global games
    print('Received form: {}'.format(request.form))
    characters = string.ascii_uppercase + string.digits
    game_id = ''.join(random.choice(characters) for i in range(2))
    game = Game(game_id)
    games[game_id] = game
    session['game_id'] = game_id
    player_name = request.form['player_name']
    session['player_name'] = player_name
    player_object = games[game_id].add_player(player_name)
    players[player_name] = player_object
    session['host'] = True
    print('CREATEGAME Session data: {}'.format(session))
    messages[game_id] = ''
    gameMessage(game_id, 'Waiting for players.')
    return redirect(url_for('play'))


@app.route('/api/joinGame', methods=['POST'])
def joinGame():
    print('Received form: {}'.format(request.form))
    game_id = request.form['game_id']
    player_name = request.form['player_name']
    session['player_name'] = player_name
    session['game_id'] = game_id
    # If this player is not already in the game, add them
    if player_name not in players:
        player_object = games[game_id].add_player(player_name)
        players[player_name] = player_object
    if player_name not in players or 'host' not in session:
        session['host'] = False
    print('JOINGAME Session data: {}'.format(session))
    game = games[game_id]
    gameMessage(game_id, '{} has joined the game!'.format(player_name))
    return redirect(url_for('play'))


@app.route('/api/startGame', methods=['POST'])
def startGame():
    game_id = session['game_id']
    print('Game {} started'.format(game_id))
    game = games[game_id]
    game.started = True
    gameMessage(game_id, 'The game has started!')
    for player_name, player in game.players.items():
        showHand(game_id, player_name)
    return ''


@app.route('/api/showHand/<game_id>/<player_name>', methods=['GET'])
def showHand(game_id, player_name):
    print('showing hand of player {} in game {}'.format(player_name, game_id))
    game = games[game_id]
    player_object = players[player_name]
    data = {
        'card1': '{}'.format(player_object.hand[0]),
        'card2': '{}'.format(player_object.hand[1]),
        'card3': '{}'.format(player_object.hand[2]),
        'card4': '{}'.format(player_object.hand[3]),
        'card5': '{}'.format(player_object.hand[4]),
        'card6': '{}'.format(player_object.hand[5]),

    }
    pusher.trigger('dixit-{}-{}'.format(player_name, game_id), 'showHand', data)
    return jsonify(data)


def gameMessage(game_id, gameMessage):
    print('Sending message to all players in game {}'.format(game_id))
    game = games[game_id]
    if messages[game_id] == '':
        messages[game_id] = gameMessage
    else:
        messages[game_id] += '<br>{}'.format(gameMessage)
    data = {
        'gameMessage': messages[game_id],
    }
    pusher.trigger('dixit-{}'.format(game_id), 'gameMessage', data)
    return jsonify(data)


app.run(host='0.0.0.0', debug=True)