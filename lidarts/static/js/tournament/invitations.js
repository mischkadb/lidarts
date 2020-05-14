$(document).ready(function() {
    // namespace for handling
    namespace = '/chat';

    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace, {transports: ['websocket']});
 
    $('.button-accept-tournament-invitation').click( function (event) {
        var hashid = this.id.replace('button-accept-tournament-invitation-', '');
        socket.emit('accept_tournament_invitation', {hashid: hashid}, function () {
            $('#element-tournament-invitation-' + hashid).html('<strong style="color: #449944">Invitation accepted.</strong>');
        });
    });

    $('.button-decline-tournament-invitation').click( function (event) {
        var hashid = this.id.replace('button-decline-tournament-invitation-', '');
        socket.emit('decline_tournament_invitation', {hashid: hashid}, function () {
            $('#element-tournament-invitation-' + hashid).html('<strong style="color: #bb4444">Invitation declined.</strong>');
        });
    });


});
