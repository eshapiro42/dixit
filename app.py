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


class AppError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['Error'] = self.message
        return rv


@app.errorhandler(AppError)
def handle_app_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


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
        'creator': session['creator'],
        'started': games[session['game_id']].started,
        'random_number': random.randint(10000000, 99999999),
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
    session['creator'] = True
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
        if player_object is None:
            raise AppError('Could not add player. Game {} has already started.'.format(game_id))
        players[player_name] = player_object
    if player_name not in players or 'creator' not in session:
        session['creator'] = False
    print('JOINGAME Session data: {}'.format(session))
    gameMessage(game_id, '{} has joined the game.'.format(player_name))
    return redirect(url_for('play'))


@app.route('/api/startGame', methods=['POST'])
def startGame():
    game_id = session['game_id']
    game = games[game_id]
    if game.started:
        return ''
    ret = game.start_game()
    # TODO: uncomment this to make the game require four players
    # if ret is None:
    #     gameMessage(game_id, 'You cannot start this game with less than four players.')
    #     return ''
    print('Game {} started'.format(game_id))
    gameMessage(game_id, 'The game has started.')
    for player_name in game.players.keys():
        showHand(game_id, player_name)
    data = {
        'started': True,
        'num_players': game.num_players,
    }
    pusher.trigger('dixit-{}'.format(game_id), 'started', data)
    game.new_round()
    scoreUpdate(game_id)
    hostTurn(game_id, game.current_host.name)
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
    player_name = session['player_name']
    game = games[game_id]
    game.host_card = request.form['hostCard']
    game.host_prompt = request.form['hostPrompt']
    card = players[player_name].play_card(game.host_card)
    showHand(game_id, player_name)
    game.table[player_name] = card
    message = '''{}'s prompt: "{}"'''.format(game.host, game.host_prompt)
    gameMessage(game_id, message, bold=True)
    othersTurn(game_id)
    return ''


@app.route('/api/sendOthersChoicesToServer', methods=['POST'])
def sendOthersChoicesToServer():
    game_id = session['game_id']
    player_name = session['player_name']
    game = games[game_id]
    others_card = request.form['othersCard']
    card = players[player_name].play_card(others_card)
    showHand(game_id, player_name)
    game.table[player_name] = card
    if len(game.table) == game.num_players:
        showTable(game_id)
        othersVote(game_id)
    return ''


@app.route('/api/sendOthersVotesToServer', methods=['POST'])
def sendOthersVotesToServer():
    game_id = session['game_id']
    player_name = session['player_name']
    game = games[game_id]
    others_card = request.form['othersCard']
    game.votes[player_name] = others_card
    print('Player {} voted for card {}'.format(player_name, others_card))
    if len(game.votes) == game.num_players - 1:
        gameMessage(game_id, 'Everyone has voted and the results are in.')
        print('table: {}'.format(game.table))
        print('votes: {}'.format(game.votes))
        # Scoring logic
        correct_card = game.table[game.current_host.name]
        correct_count = list(game.votes.values()).count(correct_card)
        if correct_count == game.num_players - 1:
            print('Everyone guessed correctly')
            all_correct = True
            none_correct = False
        elif correct_count == 0:
            print('Nobody guessed correctly')
            all_correct = False
            none_correct = True
        else:
            print('The host won')
            all_correct = False
            none_correct = False
        for player_name, player_object in game.players.items():
            print(player_object, game.current_host)
            if player_object == game.current_host:
                # The host gets three points if some but not all of the other players voted for his choice
                if 0 < correct_count < game.num_players - 1:
                    player_object.score += 3
                    print('The host {} gets 3 points for a new score of {}'.format(player_name, player_object.score))
                    host_won = True
            elif all_correct:
                # If everyone guesses the host's choice, all other players get two points
                player_object.score += 2
                print('Everybody guessed correctly so {} gets 2 points for a new score of {}'.format(player_name, player_object.score))
            elif none_correct:
                # If no one guesses the host's choice, all other players get two points
                player_object.score += 2
                print('Nobody guessed correctly so {} gets 2 points for a new score of {}'.format(player_name, player_object.score))
                # Other players get one point if another player voted for their card
                player_card = game.table[player_name]
                votes_for_player = list(game.votes.values()).count(player_card)
                if votes_for_player > 0:
                    player_object.score += votes_for_player
                    print("Player {}'s card got {} votes for a new score of {}".format(player_name, votes_for_player, player_object.score))
            else:
                # If the host won, other players get three points for voting for the correct card
                if game.votes[player_name] == correct_card:
                    player_object.score += 3
                    print('Player {} gets 3 points for voting for the correct card for a new score of {}'.format(player_name, player_object.score))
                # Other players get one point if another player voted for their card
                player_card = game.table[player_name]
                votes_for_player = list(game.votes.values()).count(player_card)
                if votes_for_player > 0:
                    player_object.score += votes_for_player
                    print("Player {}'s card got {} votes for a new score of {}".format(player_name, votes_for_player, player_object.score))
        sendOutcomes(game_id)
        scoreUpdate(game_id)
        # Scoring is complete, so start the next round!
        game.new_round()
        hostTurn(game_id, game.current_host.name)
    return ''


def hostTurn(game_id, host_name):
    games[game_id].host = host_name
    gameMessage(game_id, "It is {}'s turn to choose a card and give a prompt.".format(host_name))
    data = {
        'host': host_name,
    }
    pusher.trigger('dixit-{}'.format(game_id), 'hostTurn', data)


def othersTurn(game_id):
    message = "Other players, choose a card to match the prompt."
    gameMessage(game_id, message)
    pusher.trigger('dixit-{}'.format(game_id), 'othersTurn', None)


def othersVote(game_id):
    message = "Other players, vote for which card you think matches the prompt."
    gameMessage(game_id, message)
    pusher.trigger('dixit-{}'.format(game_id), 'othersVote', None)


def showHand(game_id, player_name):
    print('showing hand of player {} in game {}'.format(player_name, game_id))
    game = games[game_id]
    player_object = players[player_name]
    data = {}
    cardnum = 1
    for card in player_object.hand:
        data['hand{}'.format(cardnum)] = card
        cardnum += 1
    pusher.trigger('dixit-{}-{}'.format(player_name, game_id), 'showHand', data)


def showTable(game_id):
    print('showing table in game {}'.format(game_id))
    game = games[game_id]
    data = {}
    cardnum = 1
    table_list = list(game.table.values())
    random.shuffle(table_list)
    for card in table_list:
        data['table{}'.format(cardnum)] = card
        cardnum += 1
    pusher.trigger('dixit-{}'.format(game_id), 'showTable', data)


def gameMessage(game_id, gameMessage, bold=False):
    print('Sending message to all players in game {}'.format(game_id))
    game = games[game_id]
    if messages[game_id] == '':
        messages[game_id] = gameMessage
    elif gameMessage == None:
        pass
    else:
        if bold:
            messages[game_id] += '<br><b>{}</b>'.format(gameMessage)
        else:
            messages[game_id] += '<br>{}'.format(gameMessage)
    data = {
        'gameMessage': messages[game_id],
    }
    pusher.trigger('dixit-{}'.format(game_id), 'gameMessage', data)


def sendOutcomes(game_id):
    print('Sending outcomes to all players in game {}'.format(game_id))
    game = games[game_id]
    data = {
        'cardPlayers': game.table,
        'cardVoters': game.votes,
        'host': game.current_host.name,
    }
    pusher.trigger('dixit-{}'.format(game_id), 'sendOutcomes', data)


def scoreUpdate(game_id):
    print('Sending scores to all players in game {}'.format(game_id))
    game = games[game_id]
    score_html = '<tr>'
    for player_object in game.players.values():
        score_html += '\n<td> {} </td>'.format(player_object.name)
    score_html += '\n</tr>\n<tr>'
    for player_object in game.players.values():
        score_html += '\n<td> {} </td>'.format(player_object.score)
    score_html += '\n</tr>'
    data = {
        'scores': score_html,
    }
    pusher.trigger('dixit-{}'.format(game_id), 'scoreUpdate', data)


app.run(host='0.0.0.0', debug=True)