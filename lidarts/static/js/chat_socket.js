$(document).ready(function() {

    // Scroll chatbox to bottom (latest message)
    var chatbox = document.getElementById("chatbox");
    chatbox.scrollTop = chatbox.scrollHeight;

    // namespace for handling
    namespace = '/chat';

    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace, {transports: ['websocket']});

    var user_id = $('#user_id').data()['id'];
    var profile_url = $('#profile_url').data()['url'];
    var game_url = $('#game_url').data()['url'];
    var create_url = $('#create_url').data()['url'] + '/x01/';
    var private_messages_url = $('#private_messages_url').data()['url'];
    var match_alerts_enabled = true;
    if ($('#match_alert').data()['enabled'] == 'False') {
        match_alerts_enabled = false;
    }

    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    socket.on('connect', function () {
    });

    socket.on('send_online_players', function (msg) {
        $('#online_players').html('');
        var user;
        for (user in msg['players']){
            // no border for lidarts logo as flag
            if (msg['players'][user]['country'] == 'lidarts') {
                country_flag_class = '';
            } else {
                country_flag_class = 'country-flag';
            }

            if (msg['players'][user]['country'] != null) {
                flag = '<img src="/static/img/flags/' + msg['players'][user]['country'] + '.png" style="margin-right: 3px" class="' + country_flag_class + '">'
            } else {
                flag = ''
            };
            $('#online_players').append('<div class="card"><div class="card-body" style="padding: 2px 2px 2px 2px;">'
                + '<strong style="font-size: 20px;"><a href="' + profile_url + msg['players'][user]['username'] + '" id="powertip-' + user + '" class="tooltips text-secondary" data-powertip="">'
                + '<img src="' + msg['players'][user]['avatar'] + '" height="50px" width="50px" class="avatar avatar-status avatar-status-' + msg['players'][user]['status'] + '">'
                + flag
                + msg['players'][user]['username'] + '</a></strong>');
            $('#powertip-' + user).powerTip({placement: 'w', mouseOnToPopup: 'True'});
            if (user_id == msg['players'][user]['id']) {
                $('#powertip-' + user).data('powertip', '<div><span class="text-dark font-weight-bold">' +
                    '<i class="fas fa-circle status-' + msg['players'][user]['status'] + ' powerTip-status"></i>' +
                    '<a href="' + profile_url + msg['players'][user]['username'] + '" class="text-dark">' + msg['players'][user]['username'] + '</a></span></div>' +
                    '<hr style="margin: 2px 0px 5px 0px;">' +
                    '<span class="text-dark">Avg.: ' + msg['players'][user]['statistics']['average'] + ' | Doubles: ' + msg['players'][user]['statistics']['doubles'] + '%</span>' +
                    '<hr style="margin: 2px 0px 5px 0px;">' +
                    '<div class="text-secondary">This is you.</div></div></div>');
            } else {
                $('#powertip-' + user).data('powertip', '<div><span class="text-dark">' +
                    '<i class="fas fa-circle status-' + msg['players'][user]['status'] + ' powerTip-status"></i>' +
                    '<a href="' + profile_url + msg['players'][user]['username'] + '" class="text-dark">' + msg['players'][user]['username'] + '</a></span></div>' +
                    '<hr style="margin: 2px 0px 5px 0px;">' +
                    '<span class="text-dark">Avg.: ' + msg['players'][user]['statistics']['average'] + ' | Doubles: ' + msg['players'][user]['statistics']['doubles'] + '%</span>' +
                    '<hr style="margin: 2px 0px 5px 0px;">' +
                    '<div class="btn-group powertip-buttons">' +
                    '<a href="' + create_url + msg['players'][user]['username'] + '" class="btn btn-secondary" role="button" title="Challenge to a game"><i class="fas fa-dice"></i></a>' +
                    '<a href="' + private_messages_url + '" role="button" class="btn btn-secondary" title="Send private message"><i class="fas fa-comments"></i></a>' +
                    '<button type="button" class="btn btn-secondary button-send-friend-request" id="button-send-friend-request-' + msg['players'][user]['id'] + '" title="Send friend request"><i class="fas fa-user-friends"></i></button>' +
                    '</div></div></div>');
            }
        };
        $('#online-players-count').html(msg['online-count']);
        $('#ingame-players-count').html(msg['ingame-count']);

    });

    $(document).on('click', '.button-send-friend-request', function (event) {
        var send_request_url = $('#send_request_url').data()['url'];
        var id = this.id.replace('button-send-friend-request-', '');

        $.post(send_request_url + id,
            function() {
                $(document.getElementById('button-send-friend-request-' + id)).html('<i class="fas fa-check text-success"></i>');
            }
        );
    });


    socket.on('send_message', function (msg) {
        // allow 1px inaccuracy by adding 1
        var isScrolledToBottom = chatbox.scrollHeight - chatbox.clientHeight <= chatbox.scrollTop + 1;
        if (msg['country'] == 'lidarts') {
            country_flag_class = '';
        } else {
            country_flag_class = 'country-flag';
        }

        if (msg['country'] != null) {
            flag = '<img src="/static/img/flags/' + msg['country'] + '.png" style="margin-right: 5px" class="' + country_flag_class + '">'
        } else {
            flag = ''
        }
        console.log(flag);
        $('#chatbox').append('<p>' + flag + '<strong><a href="' + profile_url +
            msg['author'] +
            '" class="text-dark">' + msg['author'] + '</a></strong> <small class="text-secondary">' +
            moment(msg['timestamp']).local().format('HH:mm:ss')
            + ' - Avg.: ' + msg['statistics']['average'] + '</small><br>' +
            msg['message'] + '</p><hr>'
        );

        if(isScrolledToBottom)
            chatbox.scrollTop = chatbox.scrollHeight - chatbox.clientHeight;
    });


    socket.on('send_system_message_new_game', function (msg) {
        // allow 1px inaccuracy by adding 1
        var isScrolledToBottom = chatbox.scrollHeight - chatbox.clientHeight <= chatbox.scrollTop + 1;

        $('#new-games-box').prepend(
            '<p style="margin-bottom: 5px"><strong>'
            + '<a href="' + profile_url + msg['p1_name'] +'" class="text-secondary">'
            + msg['p1_name']
            + '</a></strong> vs. <strong><a href="' + profile_url + msg['p2_name'] +'" class="text-secondary">'
            + msg['p2_name']
            + '</a></strong> <a href="' + game_url + msg['hashid'] + '">Watch</a></p>'
            + '<hr style="margin-top: 5px; margin-bottom: 5px;">'
        );

        if(isScrolledToBottom)
            chatbox.scrollTop = chatbox.scrollHeight - chatbox.clientHeight;        
    });


    socket.on('send_system_message_game_completed', function (msg) {
        if (match_alerts_enabled == false) {
            return;
        };     
        
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

        $('#latest-results-box').prepend('<p style="margin-bottom: 5px"><strong>' +
            '<a href="' + profile_url + msg['p1_name'] +'" style="color: ' + color1 + '">'
            + msg['p1_name'] + '</a></strong> ' 
            + msg['p1_score'] + ':' + msg['p2_score']
            + ' <strong>' +
            '<a href="' + profile_url + msg['p2_name'] +'" style="color: ' + color2 + '">' +
            msg['p2_name'] +
            '</a></strong>'
            + '<a href="' + game_url + msg['hashid'] + '"> Details</a></p>'
            + '<hr style="margin-top: 5px; margin-bottom: 5px;">'

        );

        if(isScrolledToBottom)
            chatbox.scrollTop = chatbox.scrollHeight - chatbox.clientHeight;
    });



    // Handler for the score input form.
    var validation_url = $('#validation_url').data();
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
                        message: $('#message').val(), user_id: user_id
                    });
                } else {
                }
                $('input[name=message]').val('');
            });
        return false;
    });

    $('#match-alert-toggle').click(function() {
        if ($('#match-alert-toggle').hasClass('active') == true) {
            $('#match-alert-toggle').html('Match alerts disabled');
            match_alerts_enabled = false;
            socket.emit('disable_match_alert');
        } else {
            $('#match-alert-toggle').html('Match alerts enabled');
            match_alerts_enabled = true;
            socket.emit('enable_match_alert');
        }
    });

    $('#left-column-toggle').click(function() {
        $('#latest-results-window').toggleClass("d-block");
        $('#latest-results-window').toggleClass("d-none");
        $('#new-games-window').toggleClass("d-block");
        $('#new-games-window').toggleClass("d-none");
        $('#public-challenge-window').toggleClass("d-block");
        $('#public-challenge-window').toggleClass("d-none");
    });

    

});



