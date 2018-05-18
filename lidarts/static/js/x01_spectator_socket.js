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
    socket.on('score_response', function(msg) {
        $('#p1_score').html(msg.p1_score);
        $('#p2_score').html(msg.p2_score);
        $('#p1_sets').html(msg.p1_sets);
        $('#p2_sets').html(msg.p2_sets);
        $('#p1_legs').html(msg.p1_legs);
        $('#p2_legs').html(msg.p2_legs);
    });
    socket.on('game_completed', function() {
        console.log('Game completed')
        $('#confirm_completion').show()
    });

});