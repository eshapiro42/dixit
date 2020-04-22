Pusher.logToConsole = true;

var pusher = new Pusher('aac926d8b7731623a59a', {
    cluster: 'us3'
});

var myChannel;
var gameChannel;
var num_players;

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

$("#startGameButton").bind("click", function() {
    $.ajax({
        type: 'POST',
        url: '/api/startGame',
    });
});

$(window).bind("load", function() {
    var myChannelName = player_name.replace(/ /g,"_");
    myChannel = pusher.subscribe(`dixit-${myChannelName}-${game_id}`);
    gameChannel = pusher.subscribe(`dixit-${game_id}`);

    gameChannel.bind('gamePlayable', data => {
        if (creator == player_name && started == "False") {
            $("#startGameButton").show();
        }
    });
    
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
        started = data.started;
        num_players = data.num_players;
        $("#startGameButton").hide();
        clearTable();
        createTable(num_players);
        $("#tablecontainer").show();
        $("#handcontainer").show();
        $("#scorecontainer").show();
    });
    
    gameChannel.bind('startHostTurn', data => {
        if (data.host == player_name) {
            $('.hand-card').bind('click.hostTurn', function() {
                var hostCard = $(this).children($('img')).attr('cardnum');
                var hostPrompt;
                do {
                    hostPrompt = prompt("Please enter your prompt", "");
                } while(hostPrompt == "");
                if (hostPrompt == null) {
                    return;
                }
                sendHostChoice(hostCard, hostPrompt);
                $('.hand-card').unbind('.hostTurn');
            });
            alert('It is your turn!');
        }
    });
    
    gameChannel.bind('startOtherTurn', data => {
        if (data.host != player_name) {
            $('.hand-card').bind('click.otherTurn', function() {
                var card = $(this).children($('img')).attr('cardnum');
                sendOtherChoice(card);
                $('.hand-card').unbind('.otherTurn');
            });
        }
    });
    
    gameChannel.bind('startVoting', data => {
        if (data.host != player_name) {
            $('.table-card').bind('click.voting', function() {
                var vote = $(this).children($('img')).attr('cardnum');
                $(this).addClass("border-info");
                sendVote(vote);
                $('.table-card').unbind('.voting');
            });
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

    gameChannel.bind('pusher:subscription_succeeded', function() {
        getMessages();
    });

});