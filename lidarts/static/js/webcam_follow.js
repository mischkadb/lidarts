$(document).ready(function() {
    var hashid = $('#jitsi-settings').data()['hashid'];
    var currentuser_id = $('#user_id').data()['id'];
    // namespace for handling
    namespace = '/webcam_follow';

    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace, {transports: ['websocket']});

    socket.on('force_reload', function () {
        console.log('reload');
        location.reload();
    });   

});



