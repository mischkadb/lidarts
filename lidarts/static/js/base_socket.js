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

    socket.emit('get_status');

    socket.on('status_reply', function (msg) {
        var indicator = $(document.getElementsByClassName('status-indicator'));
        indicator.addClass('status-' + msg['status']);
    });

    socket.on('send_notification', function (msg) {
        if ($('#notification-badge').text() == '') {
            $('#notification-badge').text('1');
        } else{
            $('#notification-badge').text(parseInt($('#notification-badge').text())+1);
        }
        $('#no-notifications-text').hide();

        var link;
        if (msg['type'] == 'challenge') {
            link = '/lobby'
        } else {
            link = '/private_messages'
        }
        $('#notification-dropdown-menu').prepend(
            '<a class="dropdown-item" href="' + link + '"><strong>' + msg['author'] + '</strong><br>'
            + msg['message'] + '</a><hr class="notification-seperator">'
        );

        var audio = new Audio('/static/sounds/notification.mp3');
        audio.play();
    });

    $('#notification-dropdown').click( function() {
        $('#notification-badge').val('');
        $.post('/notifications_read');
    });

    var status_url = $('#status_url').data()['url'];

    $('.dropdown-status').click( function (event) {
        var status = event.target.id.replace('dropdown-', '');

        $.post(status_url + status,
            function() {
                var indicator = $(document.getElementsByClassName('status-indicator'));
                indicator.removeClass('status-online');
                indicator.removeClass('status-lfg');
                indicator.removeClass('status-busy');
                indicator.addClass('status-' + status);
            });
    });


});



