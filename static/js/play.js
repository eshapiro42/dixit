Pusher.logToConsole = true;

var pusher = new Pusher('aac926d8b7731623a59a', {
    cluster: 'us3'
});

var myChannel = pusher.subscribe(`dixit-${player_name}-${game_id}`);
var gameChannel = pusher.subscribe(`dixit-${game_id}`);

var myTurn = false;

gameChannel.bind('gameMessage', data => {
    $('#gameMessage').html(data.gameMessage);
    $('#gameMessageContainer').scrollTop($('#gameMessageContainer')[0].scrollHeight);
});

gameChannel.bind('started', data => {
    started = data.started;
});

gameChannel.bind('startTurn', data => {
    if (data.host == player_name) {
        writePrompt = true;
        $('#promptInput').prop('readonly', false);
    } else {
        $('#promptInput').prop('readonly', true);
        $('#promptInput').attr('placeholder', `It is ${data.host}'s turn.`);
    }
});


myChannel.bind('showHand', data => {
    $("#handcontainer").show();
    $("#card1").attr('src', `/static/cards/${data.card1}.jpg`);
    $("#card2").attr('src', `/static/cards/${data.card2}.jpg`);
    $("#card3").attr('src', `/static/cards/${data.card3}.jpg`);
    $("#card4").attr('src', `/static/cards/${data.card4}.jpg`);
    $("#card5").attr('src', `/static/cards/${data.card5}.jpg`);
    $("#card6").attr('src', `/static/cards/${data.card6}.jpg`);
});

function startGame() {
    $.ajax({
        type: 'POST',
        url: '/api/startGame',
    });
}

function onLoad() {
    $.ajax({
        type: 'POST',
        url: '/api/onLoad',
    });
}

$(window).bind("load", function() {
    if (host == "True" && !started) {
        $("#startGameButton").show();
    }
    onLoad();
});

$("#startGameButton").bind("click", function() {
    $("#startGameButton").hide();
    startGame();
});