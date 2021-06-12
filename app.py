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

from game import Game, State


app = Flask(__name__)
try:
    app.config["SECRET_KEY"] = bytes(os.environ["SECRET_KEY"], "utf-8").decode("unicode_escape")
except KeyError:
    app.config["SECRET_KEY"] = "TEST"
random.seed()
games = {}
players = {}
creators = {}
messages = {}
pusher = Pusher(app_id="982239", key="aac926d8b7731623a59a", secret="199bad4a11c6eae764d1", cluster="us3")


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
        rv["Error"] = self.message
        return rv


def playerChannel(player_name, game_id):
    allowed_characters = string.ascii_letters + string.digits + "_-=@,.;"
    channel_name = player_name
    for character in player_name:
        if character not in allowed_characters:
            channel_name = channel_name.replace(character, "_")
    return "dixit-{}-{}".format(channel_name, game_id)


def gameChannel(game_id):
    return "dixit-{}".format(game_id)


@app.errorhandler(AppError)
def handle_app_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def index():
    session.clear()
    data = {
        "random_number": random.randint(10000000, 99999999),
    }
    return render_template("index.html", data=data)


@app.route("/play", defaults={"rejoin": False})
@app.route("/play/<rejoin>", methods=["GET", "POST"])
def play(rejoin):
    print("PLAY Session data: {}".format(session))
    print("started={}".format(games[session["game_id"]].started))
    data = {
        "player_name": session["player_name"],
        "game_id": session["game_id"],
        "creator": creators["game_id"],
        "started": games[session["game_id"]].started,
        "random_number": random.randint(10000000, 99999999),
        "rejoin": rejoin,
    }
    return render_template("play.html", data=data)


@app.route("/api/createGame", methods=["POST"])
def createGame():
    global games
    print("Received form: {}".format(request.form))
    characters = string.ascii_uppercase + string.digits
    # Create a unique Game ID
    game_id = "".join(random.choice(characters) for i in range(4))
    while game_id in games:
        game_id = "".join(random.choice(characters) for i in range(4))
    # Create the game object
    game = Game(game_id)
    # Add the game object to the global dictionary of games
    games[game_id] = game
    session["game_id"] = game_id
    player_name = str(request.form["player_name"]).strip()
    session["player_name"] = player_name
    # Add the player to the game
    player_object = game.add_player(player_name)
    # Add the player object to the global dictionary of players
    players[(player_name, game_id)] = player_object
    creators["game_id"] = player_name
    print("CREATEGAME Session data: {}".format(session))
    messages[game_id] = ""
    gameMessage(game_id, "{} created the game room.".format(player_name))
    gameMessage(game_id, "Waiting for players.")
    return redirect(url_for("play"))


@app.route("/api/joinGame", methods=["POST"])
def joinGame():
    print("Received form: {}".format(request.form))
    game_id = str(request.form["game_id"]).upper().strip()
    player_name = str(request.form["player_name"]).strip()
    session["player_name"] = player_name
    session["game_id"] = game_id
    session.modified = True
    try:
        game = games[game_id]
    except KeyError:
        raise AppError("Game ID {} was not found.".format(game_id))
    # If this player is already in the game, re-add them
    if (player_name, game_id) in players:
        rejoin = True
        gameMessage(game_id, "{} has rejoined the game.".format(player_name))
    # If this player is not already in the game, create a new player object
    else:
        rejoin = False
        player_object = game.add_player(player_name)
        if player_object is None:
            raise AppError("Could not add player. Game {} has already started.".format(game_id))
        players[(player_name, game_id)] = player_object
        gameMessage(game_id, "{} has joined the game.".format(player_name))
    print("JOINGAME Session data: {}".format(session))
    if game.playable:
        gamePlayable(game_id)
    if rejoin:
        return redirect(url_for("play", rejoin=True))
    else:
        return redirect(url_for("play"))


@app.route("/api/addCPU", methods=["POST"])
def addCPU():
    game_id = session["game_id"]
    try:
        game: Game = games[game_id]
    except KeyError:
        raise AppError("Game ID {} was not found.".format(game_id))
    player_name: str = f"CPU-{len(game.cpu_players)}"
    # Create a new player object
    player_object = game.add_player(player_name, cpu=True)
    if player_object is None:
        raise AppError("Could not add player. Game {} has already started.".format(game_id))
    players[(player_name, game_id)] = player_object
    gameMessage(game_id, "{} has joined the game.".format(player_name))
    if game.playable:
        gamePlayable(game_id)
    return ""


@app.route("/api/rejoin", methods=["POST"])
def rejoin():
    game_id = session["game_id"]
    player_name = session["player_name"]
    game = games[game_id]
    player = players[(player_name, game_id)]
    data = {
        "started": game.started,
        "num_players": game.num_players,
    }
    pusher.trigger(playerChannel(player_name, game_id), "rejoin", data)
    showHand(game_id, player_name)
    if game.state == State.HOST_CHOOSING and player == game.host:
        startHostTurn(game_id)
    elif game.state == State.OTHERS_CHOOSING and player != game.host:
        startOtherTurn(game_id)
    elif game.state == State.VOTING and player != game.host:
        startVoting(game_id)
    else:
        sendOutcomes(game_id)
    return ""


@app.route("/api/startGame", methods=["POST"])
def startGame():
    game_id = session["game_id"]
    game = games[game_id]
    if game.started:
        return ""
    ret = game.start()
    if ret is None:
        raise AppError("You cannot start a game with fewer than four players")
    print("Game {} started".format(game_id))
    gameMessage(game_id, "The game has started.")
    data = {
        "started": True,
        "num_players": game.num_players,
    }
    pusher.trigger(gameChannel(game_id), "started", data)
    if game.state == State.HOST_CHOOSING:
        showHands(game_id)
        startHostTurn(game_id)
    return ""


@app.route("/api/getMessages")
def getMessages():
    game_id = session["game_id"]
    gameMessage(game_id, None)
    return ""


@app.route("/api/sendHostChoice", methods=["POST"])
def sendHostChoice():
    game_id = session["game_id"]
    player_name = session["player_name"]
    game: Game = games[game_id]
    host_card = request.form["hostCard"]
    host_prompt = request.form["hostPrompt"]
    print("Host {} chose card {}".format(player_name, host_card))
    game.current_round.hostChoice(host_card, host_prompt)
    showHand(game_id, player_name)
    message = '''{}'s prompt: "{}"'''.format(game.host.name, game.current_round.host_prompt)
    hostPrompt(game_id, host_prompt)
    gameMessage(game_id, message, bold=True)
    if game.state == State.OTHERS_CHOOSING:
        startOtherTurn(game_id)
    return ""


@app.route("/api/sendOtherChoice", methods=["POST"])
def sendOtherChoice():
    game_id = session["game_id"]
    player_name = session["player_name"]
    player = players[(player_name, game_id)]
    game: Game = games[game_id]
    card = request.form["card"]
    print("Player {} chose card {}".format(player_name, card))
    game.current_round.otherChoice(player, card)
    showHand(game_id, player_name)
    message = """{} played a card.""".format(player_name)
    gameMessage(game_id, message)
    if game.state == State.CPUS_CHOOSING:
        for cpu_player in game.cpu_players:
            game.current_round.cpuChoice(cpu_player)
            message = """{} played a card.""".format(cpu_player.name)
            gameMessage(game_id, message)
        game.loop.send(None)
        startVoting(game_id)
    return ""


@app.route("/api/sendVote", methods=["POST"])
def sendVote():
    game_id = session["game_id"]
    player_name = session["player_name"]
    player = players[(player_name, game_id)]
    game: Game = games[game_id]
    vote = request.form["card"]
    print("Player {} voted for card {}".format(player_name, vote))
    game.current_round.vote(player, vote)
    message = """{} voted.""".format(player_name)
    gameMessage(game_id, message)
    if game.state == State.CPUS_VOTING:
        for cpu_player in game.cpu_players:
            game.current_round.cpuVote(cpu_player)
            message = """{} voted.""".format(cpu_player.name)
            gameMessage(game_id, message)
        game.loop.send(None)
        # Scoring is complete, so start the next round!
        sendOutcomes(game_id)
        scoreUpdate(game_id)
        game.current_round.end()
        startHostTurn(game_id)
    return ""


@app.route("/api/sendMulligan", methods=["POST"])
def sendMulligan():
    game_id = session["game_id"]
    player_name = session["player_name"]
    player = players[(player_name, game_id)]
    game = games[game_id]
    card = request.form["card"]
    print("Player {} mulliganed card {}".format(player_name, card))
    player.discard_card(card)
    player.draw_card()
    showHand(game_id, player_name)
    message = """{} used a mulligan.""".format(player_name)
    gameMessage(game_id, message)
    return ""


def startHostTurn(game_id):
    game = games[game_id]
    host_name = game.host.name
    gameMessage(game_id, "It is {}'s turn to choose a card and give a prompt.".format(host_name))
    data = {
        "host": host_name,
    }
    pusher.trigger(gameChannel(game_id), "startHostTurn", data)


def startOtherTurn(game_id):
    game = games[game_id]
    host_name = game.host.name
    message = "Other players, choose a card to match the prompt."
    gameMessage(game_id, message)
    data = {
        "host": host_name,
    }
    pusher.trigger(gameChannel(game_id), "startOtherTurn", data)


def startVoting(game_id):
    game = games[game_id]
    host_name = game.host.name
    message = "Other players, vote for which card you think matches the prompt."
    gameMessage(game_id, message)
    data = {
        "host": host_name,
    }
    showTable(game_id)
    pusher.trigger(gameChannel(game_id), "startVoting", data)


def showHand(game_id, player_name):
    print("showing hand of player {} in game {}".format(player_name, game_id))
    player = players[(player_name, game_id)]
    pusher.trigger(playerChannel(player_name, game_id), "showHand", player.hand)


def showHands(game_id):
    game = games[game_id]
    for player in game.players:
        showHand(game_id, player.name)


def showTable(game_id):
    print("showing table in game {}".format(game_id))
    game = games[game_id]
    cardnum = 1
    table_list = list(game.table.values())
    random.shuffle(table_list)
    pusher.trigger(gameChannel(game_id), "showTable", table_list)


def gameMessage(game_id, gameMessage, bold=False):
    print("Sending message to all players in game {}: {}".format(game_id, gameMessage))
    game = games[game_id]
    if messages[game_id] == "":
        messages[game_id] = gameMessage
    elif gameMessage == None:
        pass
    else:
        if bold:
            messages[game_id] += "<br><b>{}</b>".format(gameMessage)
        else:
            messages[game_id] += "<br>{}".format(gameMessage)
    data = {
        "gameMessage": messages[game_id],
    }
    pusher.trigger(gameChannel(game_id), "gameMessage", data)


def hostPrompt(game_id, prompt):
    print("Sending prompt to all players in game {}: {}".format(game_id, prompt))
    data = {
        "hostPrompt": prompt,
    }
    pusher.trigger(gameChannel(game_id), "hostPrompt", data)


def sendOutcomes(game_id):
    print("Sending outcomes to all players in game {}".format(game_id))
    game = games[game_id]
    data = {
        "cardPlayers": game.table,
        "cardVoters": game.votes,
        "host": game.host.name,
    }
    pusher.trigger(gameChannel(game_id), "sendOutcomes", data)


def gamePlayable(game_id):
    print("Sending playable data to game {}".format(game_id))
    game = games[game_id]
    pusher.trigger(gameChannel(game_id), "gamePlayable", None)


def scoreUpdate(game_id):
    print("Sending scores to all players in game {}".format(game_id))
    game = games[game_id]
    score_html = "<tr>"
    for player_object in game.players:
        score_html += "\n<td> {} </td>".format(player_object.name)
    score_html += "\n</tr>\n<tr>"
    for player_object in game.players:
        score_html += "\n<td> {} </td>".format(player_object.score)
    score_html += "\n</tr>"
    data = {
        "scores": score_html,
    }
    pusher.trigger(gameChannel(game_id), "scoreUpdate", data)


if __name__ == "__main__":
    app.run()
