$(document).ready(function () {

    // namespace for the game handling
    namespace = '/base';
    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace, { transports: ['websocket'] });

    var cdn_url = '';

    if (window.location.hostname == 'lidarts.org') {
        cdn_url = 'https://lidartsstatic.org'
    }

    var notification_sound_enabled = false;
    var is_authenticated = false;
    if ($('#is_authenticated').data()['auth'] == 'True') {
        is_authenticated = true
    }
    var user_id = $('#user_id').data()['id'];
    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    socket.on('connect', function () {
        console.log('Base socket connected');
        if (is_authenticated == true) {
            socket.emit('user_heartbeat', { user_id: user_id });
            socket.emit('get_status', { user_id: user_id });
            socket.emit('init', { user_id: user_id });
        }
    });

    socket.on('disconnect', function () {
        console.log('Base socket disconnected');
    });

    socket.on('settings', function (msg) {
        notification_sound_enabled = msg['notification_sound'];
    });

    if (is_authenticated == true) {
        window.setInterval(function () {
            socket.emit('user_heartbeat', { user_id: user_id });
        }, 30000);
    }

    socket.on('status_reply', function (msg) {
        var indicator = $(document.getElementsByClassName('status-indicator'));
        indicator.addClass('status-' + msg['status']);
    });

    socket.on('send_notification', function (msg) {
        if ($('#notification-badge').text() == '') {
            $('#notification-badge').text('1');
        } else {
            $('#notification-badge').text(parseInt($('#notification-badge').text()) + 1);
        }
        $('#no-notifications-text').hide();

        var link;
        if (msg['type'] == 'challenge') {
            link = '/lobby'
        } else {
            link = '/private_messages'
        }
        if (msg['webcam'] == true) {
            webcam_icon = ' <i class="fas fa-camera fa-xs"></i> '
        } else {
            webcam_icon = ''
        }


        $('#notification-dropdown-menu').prepend(
            '<a class="dropdown-item" href="' + link + '"><strong>' + msg['author'] + '</strong><br>'
            + msg['message'] + webcam_icon + '</a><hr class="notification-seperator">'
        );

        if (notification_sound_enabled == true && msg['silent'] == false) {
            var audio = new Audio(cdn_url + '/static/sounds/notification.mp3');
            audio.play();
        }

    });

    $('#notification-dropdown').click(function () {
        $('#notification-badge').val('');
        $.post('/notifications_read');
    });

    var status_url = $('#status_url').data()['url'];

    $('.dropdown-status').click(function (event) {
        var status = this.id.replace('dropdown-', '');

        $.post(status_url + status,
            function () {
                var indicator = $(document.getElementsByClassName('status-indicator'));
                indicator.removeClass('status-online');
                indicator.removeClass('status-lfg');
                indicator.removeClass('status-busy');
                indicator.addClass('status-' + status);
            });
    });

    $(function () {
        $('[data-toggle="popover"]').popover()
    })

    $('.popover-dismiss').popover({
        trigger: 'focus'
    })


});
