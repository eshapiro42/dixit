$("#createGameButton").bind('click', function() {
    setTimeout(function() {
        $("#createGamePlayerNameInput:text:visible:first").focus();
    }, 100);
});

$("#joinGameButton").bind('click', function() {
    setTimeout(function() {
        $("#joinGamePlayerNameInput:text:visible:first").focus();
    }, 100);
});