Pusher.logToConsole = true;

var pusher = new Pusher('aac926d8b7731623a59a', {
    cluster: 'us3'
});

var myChannel = pusher.subscribe(`dixit-${player_name}-${game_id}`);
var gameChannel = pusher.subscribe(`dixit-${game_id}`);

var youAreHost = false;
var hostWent = false;

gameChannel.bind('gameMessage', data => {
    $('#gameMessage').html(data.gameMessage);
    $('#gameMessageContainer').scrollTop($('#gameMessageContainer')[0].scrollHeight);
});

gameChannel.bind('started', data => {
    started = data.started;
    $("#startGameButton").hide();
    clearTable();
    $("#tablecontainer").show();
    $("#handcontainer").show();
});

gameChannel.bind('startTurn', data => {
    if (data.host == player_name) {
        youAreHost = true;
    }
});

gameChannel.bind('hostPromptReceivedByClient', data => {
    promptText = `${data.host}'s prompt: "${data.prompt}"`
    $("#promptContainer").html(promptText);
    $("#promptContainer").show();
});

$('.hand-card').bind('click', function() {
    if (youAreHost && !hostWent) {
        youAreHost = false;
        hostWent = true;
        var hostCard = $(this).children($('img')).attr('cardnum');
        var hostPrompt = prompt("Please enter your prompt", "");
        sendHostChoices(hostCard, hostPrompt);
    }
});

$('.table-card').bind('click', function() {
    if (selectCardFromTable) {
        alert($(this).children($('img')).attr('cardnum'));
        selectCardFromTable = false;
    }
});

myChannel.bind('showHand', data => {
    $("#hand1").attr('src', `/static/cards/${data.hand1}.jpg`);
    $("#hand2").attr('src', `/static/cards/${data.hand2}.jpg`);
    $("#hand3").attr('src', `/static/cards/${data.hand3}.jpg`);    
    $("#hand4").attr('src', `/static/cards/${data.hand4}.jpg`);
    $("#hand5").attr('src', `/static/cards/${data.hand5}.jpg`);
    $("#hand6").attr('src', `/static/cards/${data.hand6}.jpg`);
    $("#hand1").attr('cardnum', data.hand1);
    $("#hand2").attr('cardnum', data.hand2);
    $("#hand3").attr('cardnum', data.hand3);
    $("#hand4").attr('cardnum', data.hand4);
    $("#hand5").attr('cardnum', data.hand5);
    $("#hand6").attr('cardnum', data.hand6);
});

gameChannel.bind('showTable', data => {
    $(".table-card").show();
    $("#table1").attr('src', `/static/cards/${data.table1}.jpg`);
    $("#table2").attr('src', `/static/cards/${data.table2}.jpg`);
    $("#table3").attr('src', `/static/cards/${data.table3}.jpg`);    
    $("#table4").attr('src', `/static/cards/${data.table4}.jpg`);
    $("#table5").attr('src', `/static/cards/${data.table5}.jpg`);
    $("#table6").attr('src', `/static/cards/${data.table6}.jpg`);
    $("#table1").attr('cardnum', data.table1);
    $("#table2").attr('cardnum', data.table2);
    $("#table3").attr('cardnum', data.table3);
    $("#table4").attr('cardnum', data.table4);
    $("#table5").attr('cardnum', data.table5);
    $("#table6").attr('cardnum', data.table6);
});

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

$(window).bind("load", function() {
    if (host == "True" && !started) {
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
