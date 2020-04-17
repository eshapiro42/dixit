Pusher.logToConsole = true;

var pusher = new Pusher('aac926d8b7731623a59a', {
    cluster: 'us3'
});

var channel = pusher.subscribe('dixit');

$('#createGameSubmitButton').bind('click', function() {
    $.ajax({
        type: 'POST',
        url: '/api/createGame', 
        data: $('#createGameForm').serialize(),
    });
});

$('#joinGameSubmitButton').bind('click', function() {
    $.ajax({
        type: 'POST',
        url: '/api/joinGame', 
        data: $('#joinGameForm').serialize(),
    });
});

$('#testButton').bind('click', function() {
    $.ajax({
        type: 'POST',
        url: '/api/test', 
        data: '',
    });
});

channel.bind('show-hand', function(data) {
    $("#card1").attr("src", '/static/cards/' + data.card1)
    $("#card2").attr("src", data.card2)
    $("#card3").attr("src", data.card3)
    $("#card4").attr("src", data.card4)


    alert('An event was triggered with message: ' + data.message);
});