Pusher.logToConsole = true;

var pusher = new Pusher('aac926d8b7731623a59a', {
    cluster: 'us3'
});

var myChannel = pusher.subscribe(`dixit-${player_name}-${game_id}`);
var gameChannel = pusher.subscribe(`dixit-${game_id}`);

var youAreHost = false;
var hostWent = false;
var youAreOther = false;
var otherWent = false;
var choosing = false;
var voting = false;

var num_players;

gameChannel.bind('gameMessage', data => {
    $('#gameMessage').html(data.gameMessage);
    $('#gameMessageContainer').scrollTop($('#gameMessageContainer')[0].scrollHeight);
});

gameChannel.bind('sendOutcomes', data => {
    var cardPlayers = data.cardPlayers;
    var cardVoters = data.cardVoters;
    var host = data.host;
    var cardPlayersList = Object.entries(cardPlayers)
    var cardVotersList = Object.entries(cardVoters)
    for ([player, card] of cardPlayersList) {
        if (player == host) {
            $(`[cardnum="${card}"]`).siblings(".card-body").children(".card-title").html(`${player}'s card`);
            $(`[cardnum="${card}"]`).siblings(".card-body").children(".card-title").css('color', 'red');
        } else {
            $(`[cardnum="${card}"]`).siblings(".card-body").children(".card-title").html(`${player}'s card`);
        }
    }
    $(".card-text").html('');
    for ([voter, card] of cardVotersList) {
        $(`[cardnum="${card}"]`).siblings(".card-body").children(".card-text").append(`${voter}'s vote<br>`);
    }
    $(".card-body").show();
});

gameChannel.bind('scoreUpdate', data => {
    $('#scores').html(data.scores);
});

gameChannel.bind('started', data => {
    started = data.started;
    num_players = data.num_players;
    $("#startGameButton").hide();
    clearTable();
    createTable(num_players);
    $("#tablecontainer").show();
    $("#handcontainer").show();
    $("#scorecontainer").show();

    $('.hand-card').bind('click', function() {
        if (choosing && youAreHost && !hostWent) {
            hostWent = true;
            choosing = false;
            var hostCard = $(this).children($('img')).attr('cardnum');
            var hostPrompt = prompt("Please enter your prompt", "");
            sendHostChoices(hostCard, hostPrompt);
        }
        if (choosing && youAreOther && !otherWent) {
            otherWent = true;
            choosing = false;
            var otherCard = $(this).children($('img')).attr('cardnum');
            sendOthersChoices(otherCard, player_name);
        }
    });
    
    $('.table-card').bind('click', function() {
        if (voting && youAreOther && !otherWent) {
            otherWent = true;
            voting = false;
            var otherCard = $(this).children($('img')).attr('cardnum');
            sendOthersVotes(otherCard, player_name);
            // Reset all state variables
            youAreHost = false;
            hostWent = false;
            youAreOther = false;
            otherWent = false;
            choosing = false;
            voting = false;
            // Alert
            alert("Your vote has been recorded!")
        }
    });
});

gameChannel.bind('hostTurn', data => {
    if (data.host == player_name) {
        youAreHost = true;
        hostWent = false;
        choosing = true;
    } else {
        youAreHost = false;
    }
});

gameChannel.bind('othersTurn', function() {
    if (!youAreHost) {
        youAreOther = true;
        otherWent = false;
        choosing = true;
    }
});

gameChannel.bind('othersVote', function() {
    if (!youAreHost) {
        youAreOther = true;
        otherWent = false;
        voting = true;
    }
});

gameChannel.bind('hostPromptReceivedByClient', data => {
    promptText = `${data.host}'s prompt: "${data.prompt}"`
});

myChannel.bind('showHand', data => {
    $("#hand1").attr('src', `/static/cards/${data.hand1}`);
    $("#hand2").attr('src', `/static/cards/${data.hand2}`);
    $("#hand3").attr('src', `/static/cards/${data.hand3}`);
    $("#hand4").attr('src', `/static/cards/${data.hand4}`);
    $("#hand5").attr('src', `/static/cards/${data.hand5}`);
    $("#hand6").attr('src', `/static/cards/${data.hand6}`);

    $("#hand1").attr('cardnum', data.hand1);
    $("#hand2").attr('cardnum', data.hand2);
    $("#hand3").attr('cardnum', data.hand3);
    $("#hand4").attr('cardnum', data.hand4);
    $("#hand5").attr('cardnum', data.hand5);
    $("#hand6").attr('cardnum', data.hand6);
});

gameChannel.bind('showTable', data => {
    $(".card-body").hide();
    $(".card-title").css('color', 'black');
    $(".table-card").show();
    $("#table1").attr('src', `/static/cards/${data.table1}`);
    $("#table2").attr('src', `/static/cards/${data.table2}`);
    $("#table3").attr('src', `/static/cards/${data.table3}`);    
    $("#table4").attr('src', `/static/cards/${data.table4}`);
    $("#table5").attr('src', `/static/cards/${data.table5}`);
    $("#table6").attr('src', `/static/cards/${data.table6}`);
    $("#table1").attr('cardnum', data.table1);
    $("#table2").attr('cardnum', data.table2);
    $("#table3").attr('cardnum', data.table3);
    $("#table4").attr('cardnum', data.table4);
    $("#table5").attr('cardnum', data.table5);
    $("#table6").attr('cardnum', data.table6);
});

function createTable(num_players) {
    for (num = 1; num <= num_players; num++) {
        var card_element = `
            <div class="col-sm-6 col-md-4 col-lg-2 col-centered">
                <div class="card table-card" style="display: none;">
                    <img src="" class="card-img-top" id="table${num}">
                    <div class="card-body" style="display: none;">
                        <h5 class="card-title"></h5>
                        <p class="card-text"></p>
                    </div>
                </div>
            </div>
        `;
        $("#table").append(card_element);
    }
}

function clearTable() {
    $(".table-card").hide();
}

function getMessages() {
    $.ajax({
        type: 'GET',
        url: '/api/getMessages',
    });
}

function sendHostChoices(hostCard, hostPrompt) {
    $.ajax({
        type: 'POST',
        url: '/api/sendHostChoicesToServer',
        data: {'hostCard': hostCard, 'hostPrompt': hostPrompt},
    });
}

function sendOthersChoices(othersCard, playerName) {
    $.ajax({
        type: 'POST',
        url: '/api/sendOthersChoicesToServer',
        data: {'othersCard': othersCard, 'playerName': playerName},
    });
}

function sendOthersVotes(othersCard, playerName) {
    $.ajax({
        type: 'POST',
        url: '/api/sendOthersVotesToServer',
        data: {'othersCard': othersCard, 'playerName': playerName},
    });
}

$(window).bind("load", function() {
    if (creator == "True" && started == "False") {
        $("#startGameButton").show();
    }
    getMessages();
});

$("#startGameButton").bind("click", function() {
    $.ajax({
        type: 'POST',
        url: '/api/startGame',
    });
});

$(window).bind("unload", function(){
    $.ajax({
        type: 'POST',
        url: '/api/playerLeft',
    });
});