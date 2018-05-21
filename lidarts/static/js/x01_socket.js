$(document).ready(function() {
    // Use a "/test" namespace.
    // An application can open a connection on multiple namespaces, and
    // Socket.IO will multiplex all those connections on a single
    // physical channel. If you don't care about multiple channels, you
    // can set the namespace to an empty string.
    namespace = '/game';
    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    var flaskData = $('#my-data').data();
    socket.on('connect', function() {
        socket.emit('init', {hashid: flaskData['hashid'] });
    });
    // Event handler for server sent data.
    // The callback function is invoked whenever the server emits data
    // to the client. The data is then displayed in the "Received"
    // section of the page.
    socket.on('my_response', function(msg) {
        $('#log').append('<br>' + $('<div/>').text('Received #' + msg.count + ': ' + msg.data).html());
    });
    socket.on('score_response', function(msg) {
        $('#p1_score').html(msg.p1_score);
        $('#p2_score').html(msg.p2_score);
        $('#p1_sets').html(msg.p1_sets);
        $('#p2_sets').html(msg.p2_sets);
        $('#p1_legs').html(msg.p1_legs);
        $('#p2_legs').html(msg.p2_legs);
        if (msg.p1_next_turn) {
            $('#p1_turn').addClass('bg-dark text-white');
            $('#p2_turn').removeClass('bg-dark text-white');
        } else {
            $('#p1_turn').removeClass('bg-dark text-white');
            $('#p2_turn').addClass('bg-dark text-white');
        }
    });
    socket.on('game_completed', function() {
        $('#p1_turn').removeClass('bg-dark text-white');
        $('#p2_turn').removeClass('bg-dark text-white');
        $('#score_input').hide();
        $('#confirm_completion').show();
    });
    // Handlers for the different forms in the page.
    // These accept data from the user and send it to the server in a
    // variety of ways
    var validation_url = $('#validation_url').data();
    var user_id = $('#user_id').data();
    var score_errors = [];
    $('form#score_input').submit(function(event) {
        $('#score_error').text('');
        $.post(
            validation_url,
            $("#score_input").serialize(),
            function (errors) {
                score_errors = errors
                if (jQuery.isEmptyObject(score_errors)) {
                    socket.emit('send_score', {score: $('#score_value').val(), hashid: flaskData['hashid'],
                    user_id: user_id['id']});
                } else {
                    $('#score_error').text(score_errors['score_value'][0]);
                }
                $('input[name=score_value]').val('');
            });
        return false;
    });

});