$(document).ready(function() {

    // Scroll chatbox to bottom (latest message)
    var chatbox = document.getElementById("chatbox");
    chatbox.scrollTop = chatbox.scrollHeight;

    // namespace for handling
    namespace = '/private_messages';

    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace, {transports: ['websocket']});

    var profile_url = $('#profile_url').data()['url'];
    var game_url = $('#game_url').data()['url'];
    var get_id_by_username_url = $('#get_id_by_username_url').data()['url'];

    var user_id = $('#user_id').data()['id'];

    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    socket.on('connect', function () {
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

    socket.on('broadcast_private_message', function(msg) {
        var messages_tab;
        if (msg['sender'] == user_id) {
            messages_tab = document.getElementById('messages_tab_' + msg['receiver'])
        } else {
            messages_tab = document.getElementById('messages_tab_' + msg['sender'])
        }

        var isScrolledToBottom = chatbox.scrollHeight - chatbox.clientHeight <= chatbox.scrollTop + 1;

        messages_tab.insertAdjacentHTML('beforeend', '<p><strong><a href="' + profile_url +
            msg['sender_name'] +
            '" class="text-dark">' + msg['sender_name'] + '</a></strong> <small class="text-secondary">' +
            moment(msg['timestamp']).local().format('HH:mm:ss') +
            '</small><br>' +
            msg['message'] + '</p><hr>'
        );

        if(isScrolledToBottom)
            chatbox.scrollTop = chatbox.scrollHeight - chatbox.clientHeight;
    });
    
    socket.on('receiver_PMs_disabled', function () {
        // allow 1px inaccuracy by adding 1
        var isScrolledToBottom = chatbox.scrollHeight - chatbox.clientHeight <= chatbox.scrollTop + 1;

        $('#chatbox').append('<p><strong>Receiver disabled private messages.</strong></p><hr>');

        if(isScrolledToBottom)
            chatbox.scrollTop = chatbox.scrollHeight - chatbox.clientHeight;
    });


    // Handler for the score input form.
    var submit_cooldown = false;
    $('form#message_input').submit(function (event) {
        event.preventDefault(); 
        if (submit_cooldown == true || $('#message').val().length == 0) {
            return;
        }
        var chat_partner = document.getElementsByClassName('chat-partner-active')[0].id.replace('chat_partner_', '');
        socket.emit(
            'broadcast_private_message',
            {message: $('#message').val(), receiver: chat_partner},
            function () {
                $('input[name=message]').val('');
                submit_cooldown = true;
                setTimeout(function(){ 
                    submit_cooldown = false;
                }, 300);
            }
        );       
    });

    $('#chat_partners').delegate('.chat-partner', 'click', function (event) {
        $('.chat-partner').removeClass('chat-partner-active');
        $(this).addClass('chat-partner-active');
        var partner_id = this.id.replace('chat_partner_', '');
        $('.message-tab').hide();
        $('#messages_tab_' + partner_id).show();

        chatbox.scrollTop = chatbox.scrollHeight - chatbox.clientHeight;
    });

    var compose_message_url = $('#compose_message_url').data()['url'];

    $('#compose_message').click(function (event) {
        var chat_partner_name = $('#compose_message_name').val();
        var chat_partner_id;

        $.get(get_id_by_username_url + chat_partner_name, function (msg) {
            if (msg == 'error') {
                return;
            }
            chat_partner_id = msg;
        });

        if ($('#chat_partner_' + chat_partner_id).length > 0) {
            return;
        }
        $.post(compose_message_url + chat_partner_name, function (msg) {
            if (msg == 'error') {
                return;
            }
            $('.chat-partner').removeClass('chat-partner-active');

            $('#chat_partners').prepend('<div class="card chat-partner chat-partner-active" id="chat_partner_' + chat_partner_id + '"><div class="card-body" style="padding: 2px 2px 2px 2px;">' +
                '<p><strong><h5><i class="fas fa-circle status-' + msg['status'] + '" style="font-size: 15px;"></i> ' + msg['username'] + '</h5></strong></p>'
                +'</div></div>');

            $('.message-tab').hide();
            $('#chatbox-tabs').append('<div id="messages_tab_' + chat_partner_id + '" class="message-tab">' +
                '<h5 class="card-title">Chat with ' + msg['username'] + '</h5></div>');


        });
    });





});



