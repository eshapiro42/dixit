Pusher.logToConsole = true;
Toast.setPlacement(TOAST_PLACEMENT.BOTTOM_RIGHT);

var pusher = new Pusher('aac926d8b7731623a59a', {
    cluster: 'us3'
});


var myChannel;
var gameChannel;
var num_players;

var tableZoom = 1;
var handZoom = 1;

var lastPlayedCard;
var currentHost;
var currentPrompt;

function gameStarted(data) {
    started = data.started;
    num_players = data.num_players;
    $("#startGameButton").hide();
    $("#addCPUButton").hide();
    clearTable();
    createTable(num_players);
    $("#summary").show();
    $("#tablecontainer").show();
    $("#handcontainer").show();
    $("#scorecontainer").show();

    initUI();
}

function initUI() {
    var offcanvasElementList = [].slice.call(document.querySelectorAll('.offcanvas'));
    var offcanvasList = offcanvasElementList.map(function (offcanvasEl) {
      return new bootstrap.Offcanvas(offcanvasEl)
    });
}

function createTable(num_players) {
    for (num = 1; num <= num_players; num++) {
        var card_element = `
            <div class="card table-card" style="display: none;">
                <img src="" class="card-img-top" id="table${num}">
                <div class="card-body" style="display: none;">
                    <h5 class="card-title"></h5>
                    <p class="card-text"></p>
                </div>
            </div>
        `;
        $("#table").append(card_element);
    }
    $(".table-card").attr("style", `--table-zoom:${tableZoom}; display: none;`);
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

function sendHostChoice(hostCard, hostPrompt) {
    $.ajax({
        type: 'POST',
        url: '/api/sendHostChoice',
        data: {'hostCard': hostCard, 'hostPrompt': hostPrompt},
    });
}

function sendOtherChoice(othersCard) {
    $.ajax({
        type: 'POST',
        url: '/api/sendOtherChoice',
        data: {'card': othersCard},
    });
}

function sendVote(othersCard) {
    $.ajax({
        type: 'POST',
        url: '/api/sendVote',
        data: {'card': othersCard},
    });
}

function sendMulligan(card) {
    $.ajax({
        type: 'POST',
        url: '/api/sendMulligan',
        data: {'card': card},
    });
}

function rejoin() {
    $.ajax({
        type: 'POST',
        url: '/api/rejoin',
    });
}

function rejoinActions(data) {
    started = data.started;
    if (started) {
        num_players = data.num_players;
        $("#startGameButton").hide();
        clearTable();
        createTable(num_players);
        $("#tablecontainer").show();
        $("#handcontainer").show();
        $("#scorecontainer").show();
    }
}

$("#startGameButton").bind("click", function() {
    $.ajax({
        type: 'POST',
        url: '/api/startGame',
    });
});

$("#addCPUButton").bind("click", function () {
    $.ajax({
        type: 'POST',
        url: '/api/addCPU',
    });
});

$("#tableSlider").on("input", function() {
    tableZoom = $(this).val() / 20;
    $(".table-card").attr("style", `--table-zoom:${tableZoom}`);
});

$("#handSlider").on("input", function() {
    handZoom = $(this).val() / 20;
    $(".hand-card").attr("style", `--hand-zoom:${handZoom}`);
});

window.addEventListener('beforeunload', function (e) { 
    e.preventDefault(); 
    e.returnValue = ''; 
}); 

$(window).bind("load", function() {
    var myChannelName = player_name;
    var allowed_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-=@,.;'
    for (var character of player_name) {
        if (!allowed_characters.includes(character)) {
            myChannelName = myChannelName.replaceAll(character, '_');
        }
    }
    myChannel = pusher.subscribe(`dixit-${myChannelName}-${game_id}`);
    gameChannel = pusher.subscribe(`dixit-${game_id}`);

    if (creator == player_name && started == "False") {
        $("#addCPUButton").show();
    }

    gameChannel.bind('gamePlayable', data => {
        if (creator == player_name && started == "False") {
            $("#startGameButton").show();
        }
    });
    
    gameChannel.bind('gameMessage', data => {
        $('#gameMessage').append(data.gameMessage);
        $('#gameMessageContainer').scrollTop($('#gameMessageContainer')[0].scrollHeight);
    });

    myChannel.bind('gameMessage', data => {
        $('#gameMessage').append(data.gameMessage);
        $('#gameMessageContainer').scrollTop($('#gameMessageContainer')[0].scrollHeight);
    });
    
    gameChannel.bind('sendOutcomes', data => {
        var cardPlayers = data.cardPlayers;
        var cardVoters = data.cardVoters;
        var host = data.host;
        var cardPlayersList = Object.entries(cardPlayers)
        var cardVotersList = Object.entries(cardVoters)
        $(".table-card").removeClass("border-info");
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
        gameStarted(data);
    });

    myChannel.bind('rejoin', data => {
        rejoinActions(data);
    });
    
    gameChannel.bind('startHostTurn', data => {
        var hostCard;
        currentHost = data.host;
        $("#summary_storyteller").text(currentHost);
        $("#summary_prompt").text("");
        $("#summary_phase").text(`${currentHost} is choosing a card.`);
        if (data.host == player_name) {
            $('#sendChoiceButton').show();
            $('#sendMulliganButton').show();
            $('.hand-card').bind('click.hostTurn', function() {
                $('.hand-card').removeClass("border-info");
                $(this).addClass("border-info");
                hostCard = $(this).children($('img')).attr('cardnum');
            });
            $('#sendMulliganButton').bind('click.hostTurn', function() {
                if (hostCard != null && confirm('Are you sure you want to mulligan the selected card?')) {
                    $('#sendMulliganButton').unbind('.hostTurn');
                    $('#sendMulliganButton').hide();
                    sendMulligan(hostCard);
                    $('.hand-card').removeClass("border-info");
                }
            })
            $('#sendChoiceButton').bind('click.hostTurn', function() {
                var hostPrompt;
                if (hostCard == null) {
                    return;
                }
                do {
                    hostPrompt = prompt("Please enter your prompt", "");
                } while(hostPrompt == "");
                if (hostPrompt == null) {
                    return;
                }
                $('#sendChoiceButton').unbind('.hostTurn');
                $('#sendChoiceButton').hide();
                $('#sendMulliganButton').hide();
                $('.hand-card').unbind('.hostTurn');
                sendHostChoice(hostCard, hostPrompt);
                $('.hand-card').removeClass("border-info");
            });
        }
    });
    
    gameChannel.bind('startOtherTurn', data => {
        var otherCard;
        $("#summary_prompt").text(currentPrompt);
        $("#summary_phase").text(`Other players are choosing their cards.`);
        if (data.host != player_name) {
            $('#sendChoiceButton').show();
            $('#sendMulliganButton').show();
            $('.hand-card').bind('click.otherTurn', function() {
                $('.hand-card').removeClass("border-info");
                $(this).addClass("border-info");
                otherCard = $(this).children($('img')).attr('cardnum');
                lastPlayedCard = otherCard;
            });
            $('#sendMulliganButton').bind('click.otherTurn', function() {
                if (otherCard != null && confirm('Are you sure you want to mulligan the selected card?')) {
                    $('#sendMulliganButton').unbind('.otherTurn');
                    $('#sendMulliganButton').hide();
                    sendMulligan(otherCard);
                    $('.hand-card').removeClass("border-info");
                }
            })
            $('#sendChoiceButton').bind('click.otherTurn', function() {
                if (otherCard == null) {
                    return;
                }
                $('#sendChoiceButton').unbind('.otherTurn');
                $('#sendChoiceButton').hide();
                $('#sendMulliganButton').hide();
                $('.hand-card').unbind('.otherTurn');
                sendOtherChoice(otherCard);
                $('.hand-card').removeClass("border-info");
            });
        }
    });
    
    gameChannel.bind('startVoting', data => {
        var voteCard;
        $("#summary_phase").text(`Other players are voting.`);
        if (data.host != player_name) {
            $('#sendVoteButton').show();
            $('.table-card').bind('click.voting', function() {
                $('.table-card').removeClass("border-info");
                $(this).addClass("border-info");
                voteCard = $(this).children($('img')).attr('cardnum');
            });
            $('#sendVoteButton').bind('click.voting', function() {
                if (voteCard == null) {
                    return;
                }
                if (voteCard == lastPlayedCard) {
                    return;
                }
                $('#sendVoteButton').hide();
                $('#sendVoteButton').unbind('.voting');
                $('.table-card').unbind('.voting');
                sendVote(voteCard);
            });
        }
    });
    
    gameChannel.bind('hostPrompt', data => {
        currentPrompt = data.hostPrompt;
    });
    
    myChannel.bind('showHand', data => {
        for (num = 1; num <= 6; num++) {
            var handCardID = `#hand${num}`;
            var cardNum = data[num - 1];
            $(handCardID).attr('src', `/static/cards/${cardNum}`);
            $(handCardID).attr('cardnum', cardNum);
        }
    });
    
    gameChannel.bind('showTable', data => {
        $(".card-body").hide();
        $(".card-title").css('color', 'black');
        $(".table-card").show();

        for (num = 1; num <= num_players; num++) {
            var tableCardID = `#table${num}`;
            var cardNum = data[num - 1];
            $(tableCardID).attr('src', `/static/cards/${cardNum}`);
            $(tableCardID).attr('cardnum', cardNum);
        }
    });

    gameChannel.bind('pusher:subscription_succeeded', function() {
        getMessages();
        if (rejoined == "True") {
            rejoin();
        }
    });

    $(".hand-card").attr("style", `--hand-zoom:1`);
});