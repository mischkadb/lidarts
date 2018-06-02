$(document).ready(function() {

    // namespace for the game handling
    namespace = '/base';
    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    socket.emit('user_heartbeat');

    window.setInterval(function(){
        /// call your function here
        socket.emit('user_heartbeat');
    }, 5000);


});



