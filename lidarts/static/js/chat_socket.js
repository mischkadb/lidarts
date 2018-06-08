$(document).ready(function() {

    // Scroll chatbox to bottom (latest message)
    var chatbox = document.getElementById("chatbox");
    chatbox.scrollTop = chatbox.scrollHeight;

    // namespace for handling
    namespace = '/chat';

    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    var profile_url = $('#profile_url').data()['url'];
    var game_url = $('#game_url').data()['url'];

    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    socket.on('connect', function () {
    });

    socket.on('send_online_players', function (msg) {
        $('#online_players').html('');
        var user;
        for (user in msg){
            $('#online_players').append('<div class="card"><div class="card-body" style="padding: 2px 2px 2px 2px;">' +
                '' +
                '<p><strong><h5><a href="' + profile_url + msg[user]['username'] + '" id="powertip-' + user + '" class="tooltips text-secondary" data-powertip="">'
                + '<i class="fas fa-circle status-' + msg[user]['status'] + '" style="font-size: 15px;"></i> ' + msg[user]['username'] + '</a></h5></strong></p>');
            $('#powertip-' + user).powerTip({placement: 'w', mouseOnToPopup: 'True'});
            $('#powertip-' + user).data('powertip', '<table class="table table-sm text-center text-dark"><tr><td>' +
                '<i class="fas fa-circle status-' + msg[user]['status'] + '" style="font-size: 10px;"></i></td>' +
                '<td><a href="' + profile_url + msg[user]['username'] + '">' + msg[user]['username'] + '</a></td></tr>' +
                '<tr><td><i class="fas fa-futbol"></i></td><td><i class="fas fa-plus-circle"></i></td></tr>' +
                '</table> ' +
                '</div></div>');
        }

    });


    socket.on('send_message', function (msg) {
        // allow 1px inaccuracy by adding 1
        var isScrolledToBottom = chatbox.scrollHeight - chatbox.clientHeight <= chatbox.scrollTop + 1;

        $('#chatbox').append('<p><strong><a href="' + profile_url +
            msg['author'] +
            '" class="text-dark">' + msg['author'] + '</a></strong> <small class="text-secondary">' +
            moment(msg['timestamp']).local().format('HH:mm:ss') +
            '</small><br>' +
            msg['message'] + '</p><hr>'
        );

        if(isScrolledToBottom)
            chatbox.scrollTop = chatbox.scrollHeight - chatbox.clientHeight;
    });


    socket.on('send_system_message_new_game', function (msg) {
        // allow 1px inaccuracy by adding 1
        var isScrolledToBottom = chatbox.scrollHeight - chatbox.clientHeight <= chatbox.scrollTop + 1;

        $('#chatbox').append('<p>New game between <strong><a href="' + profile_url + msg['p1_name'] +'" class="text-secondary">' +
            msg['p1_name'] +
            '</a></strong> and <strong><a href="' + profile_url + msg['p2_name'] +'" class="text-secondary">' +
            msg['p2_name'] +
            '</a></strong>. <a href="' + game_url + msg['hashid'] + '">Watch</a></p><hr>'
        );

        if(isScrolledToBottom)
            chatbox.scrollTop = chatbox.scrollHeight - chatbox.clientHeight;
    });


    socket.on('send_system_message_game_completed', function (msg) {
        // allow 1px inaccuracy by adding 1
        var isScrolledToBottom = chatbox.scrollHeight - chatbox.clientHeight <= chatbox.scrollTop + 1;
        var color1 = '#fbcc03';
        var color2 = '#fbcc03';

        if (msg['p1_score'] > msg['p2_score']) {
            color1 = '#08aa03';
            color2 = '#ce0e03';
        } else if (msg['p1_score'] < msg['p2_score']) {
            color1 = '#ce0e03';
            color2 = '#08aa03';

        }

        $('#chatbox').append('<p>Game finished: <strong>' +
            '<a href="' + profile_url + msg['p1_name'] +'" style="color: ' + color1 + '">' +
            msg['p1_name'] +
            '</a></strong> vs. <strong>' +
            '<a href="' + profile_url + msg['p2_name'] +'" style="color: ' + color2 + '">' +
            msg['p2_name'] +
            '</a></strong> (' + msg['p1_score'] + ':' + msg['p2_score'] + ') ' +
            '<a href="' + game_url + msg['hashid'] + '">Game summary</a></p><hr>'
        );

        if(isScrolledToBottom)
            chatbox.scrollTop = chatbox.scrollHeight - chatbox.clientHeight;
    });



    // Handler for the score input form.
    var validation_url = $('#validation_url').data();
    var user_id = $('#user_id').data();
    var message_errors = [];
    $('form#message_input').submit(function (event) {
        $.post(
            // Various errors that are caught if you enter something wrong.
            validation_url,
            $("#message_input").serialize(),
            function (errors) {
                message_errors = errors;
                if (jQuery.isEmptyObject(message_errors)) {
                    socket.emit('broadcast_chat_message', {
                        message: $('#message').val(), user_id: user_id['id']
                    });
                } else {
                }
                $('input[name=message]').val('');
            });
        return false;
    });

});



