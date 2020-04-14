$(document).ready(function() {
    var hashid = $('#jitsi-settings').data()['hashid'];
    var currentuser_id = $('#user_id').data()['id'];
    // namespace for handling
    namespace = '/webcam_follow';

    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace, {transports: ['websocket']});

    $('#summon-webcam').click(function() {
        socket.emit('request_camera', {hashid: hashid, user_id: currentuser_id});
    });

});



