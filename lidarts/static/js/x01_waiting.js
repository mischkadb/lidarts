$(document).ready(function() {
    // namespace for the game handling
    namespace = '/game';
    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace, {transports: ['websocket']});
    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    var hashid = $('#hash_id').data();
    socket.on('connect', function() {
        socket.emit('init', {hashid: hashid['hashid'] });
    });
    // Event handler for game start when a second player has accepted
    socket.on('start_game', function() {
       location.reload();
    });
});

function copyLink() {
   var copyText = document.getElementById("invitation_link");

  /* Select the text field */
  copyText.select();

  /* Copy the text inside the text field */
  document.execCommand("copy");
}