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
    print('started={}'.format(games[session['game_id']].started))
    data = {
        'player_name': session['player_name'],
        'game_id': session['game_id'],
        'host': session['host'],
        'started': games[session['game_id']].started,
    }
    return render_template('play.html', data=data)


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
    game = games[game_id]
    if game.started:
        return ''
    game.started = True
    print('Game {} started'.format(game_id))
    gameMessage(game_id, 'The game has started!')
    for player_name, player in game.players.items():
        showHand(game_id, player_name)
    data = {
        'started': True,
    }
    pusher.trigger('dixit-{}'.format(game_id), 'started', data)
    startTurn(game_id, list(game.players.keys())[0])
    return ''


@app.route('/api/getMessages')
def getMessages():
    game_id = session['game_id']
    gameMessage(game_id, None)
    return ''


@app.route('/api/playerLeft', methods=['POST'])
def playerLeft():
    player_name = session['player_name']
    game_id = session['game_id']
    print("Player {} left game {}".format(player_name, game_id))
    return ''


@app.route('/api/sendHostChoicesToServer', methods=['POST'])
def sendHostChoicesToServer():
    game_id = session['game_id']
    game = games[game_id]
    game.host_card = request.form['hostCard']
    game.host_prompt = request.form['hostPrompt']
    message = '''{}'s prompt: "{}"'''.format(game.host, game.host_prompt)
    gameMessage(game_id, message)
    return ''


def startTurn(game_id, host_name):
    games[game_id].host = host_name
    gameMessage(game_id, "It is {}'s turn to give a prompt.".format(host_name))
    data = {
        'host': host_name,
    }
    pusher.trigger('dixit-{}'.format(game_id), 'startTurn', data)


def showHand(game_id, player_name):
    print('showing hand of player {} in game {}'.format(player_name, game_id))
    game = games[game_id]
    player_object = players[player_name]
    data = {
        'hand1': '{}'.format(player_object.hand[0]),
        'hand2': '{}'.format(player_object.hand[1]),
        'hand3': '{}'.format(player_object.hand[2]),
        'hand4': '{}'.format(player_object.hand[3]),
        'hand5': '{}'.format(player_object.hand[4]),
        'hand6': '{}'.format(player_object.hand[5]),
    }
    pusher.trigger('dixit-{}-{}'.format(player_name, game_id), 'showHand', data)


def showTable(game_id):
    print('showing table in game {}'.format(game_id))
    game = games[game_id]
    data = {}
    cardnum = 0
    for card in game.table:
        data['table{}'.format(cardnum)] = card
        cardnum += 1
    pusher.trigger('dixit-{}'.format(game_id), 'showTable', data)


def gameMessage(game_id, gameMessage):
    print('Sending message to all players in game {}'.format(game_id))
    game = games[game_id]
    if messages[game_id] == '':
        messages[game_id] = gameMessage
    elif gameMessage == None:
        pass
    else:
        messages[game_id] += '<br>{}'.format(gameMessage)
    data = {
        'gameMessage': messages[game_id],
    }
    pusher.trigger('dixit-{}'.format(game_id), 'gameMessage', data)


app.run(host='0.0.0.0', debug=True)