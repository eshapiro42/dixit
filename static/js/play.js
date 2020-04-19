Pusher.logToConsole = true;

var pusher = new Pusher('aac926d8b7731623a59a', {
    cluster: 'us3'
});

var myChannel = pusher.subscribe(`dixit-${player_name}-${game_id}`);
var gameChannel = pusher.subscribe(`dixit-${game_id}`);

gameChannel.bind('gameMessage', data => {
    $('#gameMessage').html(data.gameMessage);
    $('#gameMessageContainer').scrollTop($('#gameMessageContainer')[0].scrollHeight);
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

$(window).bind("load", function() {
    if (host == "True" && !(started == "True")) {
        $("#startGameButton").show();
    }
    if (started == "True") {
        $("#handcontainer").show();
        $("#card1").attr('src', `/static/cards/${data.card1}.jpg`);
        $("#card2").attr('src', `/static/cards/${data.card2}.jpg`);
        $("#card3").attr('src', `/static/cards/${data.card3}.jpg`);
        $("#card4").attr('src', `/static/cards/${data.card4}.jpg`);
        $("#card5").attr('src', `/static/cards/${data.card5}.jpg`);
        $("#card6").attr('src', `/static/cards/${data.card6}.jpg`);
    }
});

$("#startGameButton").bind("click", function() {
    $("#startGameButton").hide();
    startGame();
});