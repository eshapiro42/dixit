$('#createGameSubmitButton').bind('click', function(event) {
    // event.preventDefault();
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