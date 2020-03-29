$(document).ready(function() {
    // namespace for the game handling
    namespace = '/public_challenge_waiting';
    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace, {transports: ['websocket']});
    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.

    
});