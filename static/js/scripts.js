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

channel.bind('showHand', data => {
    alert('An event was triggered with message: ' + data.message);
});
