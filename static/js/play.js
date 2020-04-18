Pusher.logToConsole = true;

var pusher = new Pusher('aac926d8b7731623a59a', {
    cluster: 'us3'
});

var channel = pusher.subscribe('dixit');
channel.bind('showHand', data => {
    alert('An event was triggered with message: ' + data.message);
});

$(document).ready(function() {
    $.ajax({
        type: 'GET',
        url: '/api/showHand',
        data: {
            "game_id": 'ABCDEF',
            "player_name": "Eric",
        }
    });
});