import os
import random
import string
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

from game import Game, Player


app = Flask(__name__)
try:
    app.config["SECRET_KEY"] = bytes(os.environ["SECRET_KEY"], "utf-8").decode("unicode_escape")
except KeyError:
    app.config["SECRET_KEY"] = "TEST"
random.seed()
games = {}
players = {}
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


@app.route("/play")
def play():
    print("PLAY Session data: {}".format(session))
    print("started={}".format(games[session["game_id"]].started))
    game_id: str = session["game_id"]
    game: Game = games[game_id]
    data = {
        "player_name": session["player_name"],
        "game_id": game_id,
        "creator": game.creator,
        "started": games[session["game_id"]].started,
        "random_number": random.randint(10000000, 99999999),
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
    game = Game(game_id, pusher)
    # Add the game object to the global dictionary of games
    games[game_id] = game
    session["game_id"] = game_id
    player_name = str(request.form["player_name"]).strip()
    session["player_name"] = player_name
    # Add the player to the game
    player_object = game.add_player(player_name, creator=True)
    # Add the player object to the global dictionary of players
    players[(player_name, game_id)] = player_object
    print("CREATEGAME Session data: {}".format(session))
    game.interactions.send_message("{} created the game room.".format(player_name))
    game.interactions.send_message("Waiting for players.")
    return redirect(url_for("play"))


@app.route("/api/joinGame", methods=["POST"])
def joinGame():
    print("Received form: {}".format(request.form))
    game_id: str = str(request.form["game_id"]).upper().strip()
    player_name = str(request.form["player_name"]).strip()
    session["player_name"] = player_name
    session["game_id"] = game_id
    session.modified = True
    try:
        game: Game = games[game_id]
    except KeyError:
        raise AppError("Game ID {} was not found.".format(game_id))
    # Create a new player object
    player_object = game.add_player(player_name)
    if player_object is None:
        raise AppError("Could not add player. Game {} has already started.".format(game_id))
    players[(player_name, game_id)] = player_object
    game.interactions.send_message("{} has joined the game.".format(player_name))
    print("JOINGAME Session data: {}".format(session))
    return redirect(url_for("play"))


@app.route("/api/addCPU", methods=["POST"])
def addCPU():
    game_id: str = session["game_id"]
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
    game.interactions.send_message("{} has joined the game.".format(player_name))
    return ""


@app.route("/api/startGame", methods=["POST"])
def startGame():
    game_id: str = session["game_id"]
    game: Game = games[game_id]
    if game.started:
        return ""
    ret = game.start()
    if ret is None:
        raise AppError("You cannot start a game with fewer than four players")
    print("Game {} started".format(game_id))
    game.interactions.send_message("The game has started.")
    return ""


@app.route("/api/getMessages")
def getMessages():
    game_id: str = session["game_id"]
    player_name: str = session["player_name"]
    player: Player = players[(player_name, game_id)]
    player.interactions.send_message_history()
    return ""


@app.route("/api/sendHostChoice", methods=["POST"])
def sendHostChoice():
    game_id: str = session["game_id"]
    player_name: str = session["player_name"]
    player: Player = players[(player_name, game_id)]
    game: Game = games[game_id]
    host_card: str = request.form["hostCard"]
    host_prompt: str = request.form["hostPrompt"]
    print("Host {} chose card {}".format(player_name, host_card))
    game.current_round.hostChoice(host_card, host_prompt)
    player.interactions.show_hand()
    message = '''{}'s prompt: "{}"'''.format(game.host.name, game.current_round.host_prompt)
    game.interactions.send_host_prompt(host_prompt)
    game.interactions.send_message(message, bold=True)
    game.loop.send(None)
    return ""


@app.route("/api/sendOtherChoice", methods=["POST"])
def sendOtherChoice():
    game_id: str = session["game_id"]
    player_name: str = session["player_name"]
    player: Player = players[(player_name, game_id)]
    game: Game = games[game_id]
    card: str = request.form["card"]
    print("Player {} chose card {}".format(player_name, card))
    game.current_round.otherChoice(player, card)
    player.interactions.show_hand()
    message = """{} played a card.""".format(player_name)
    game.interactions.send_message(message)
    game.loop.send(None)
    return ""


@app.route("/api/sendVote", methods=["POST"])
def sendVote():
    game_id: str = session["game_id"]
    player_name: str = session["player_name"]
    player = players[(player_name, game_id)]
    game: Game = games[game_id]
    vote: str = request.form["card"]
    print("Player {} voted for card {}".format(player_name, vote))
    game.current_round.vote(player, vote)
    message = """{} voted.""".format(player_name)
    game.interactions.send_message(message)
    game.loop.send(None)
    return ""


@app.route("/api/sendMulligan", methods=["POST"])
def sendMulligan():
    game_id: str = session["game_id"]
    player_name: str = session["player_name"]
    player: Player = players[(player_name, game_id)]
    game: Game = games[game_id]
    card: str = request.form["card"]
    print("Player {} mulliganed card {}".format(player_name, card))
    player.discard_card(card)
    player.draw_card()
    player.interactions.show_hand(game_id, player_name)
    message = """{} used a mulligan.""".format(player_name)
    game.interactions.send_message(message)
    return ""


if __name__ == "__main__":
    app.run()
