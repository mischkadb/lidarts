$(document).ready(function() {
    // namespace for the game handling
    namespace = '/game';
    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    var hashid = $('#hash_id').data();
    socket.on('connect', function() {
        socket.emit('init', {hashid: hashid['hashid'] });
    });
    // Event handler for server sent score data
    socket.on('score_response', function(msg) {
        $('#p1_score').html(msg.p1_score);
        $('#p2_score').html(msg.p2_score);
        $('#p1_sets').html(msg.p1_sets);
        $('#p2_sets').html(msg.p2_sets);
        $('#p1_legs').html(msg.p1_legs);
        $('#p2_legs').html(msg.p2_legs);
        // Colored turn indicators.
        if (msg.p1_next_turn) {
            $('#p1_turn').addClass('bg-dark text-white');
            $('#p2_turn').removeClass('bg-dark text-white');
        } else {
            $('#p1_turn').removeClass('bg-dark text-white');
            $('#p2_turn').addClass('bg-dark text-white');
        }
    });
    // Remove turn indicators when game is over and show link to game overview
    socket.on('game_completed', function() {
        console.log('Game completed')
        $('#confirm_completion').show()
    });

});