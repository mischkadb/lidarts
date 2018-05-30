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

    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    socket.on('connect', function () {
    });

    socket.on('send_online_players', function (msg) {
        $('#online_players').html('');
        var user;
        for (user in msg){
            $('#online_players').append('<p><strong><a href="" id="powertip-' + user + '" class="tooltips" data-powertip="">'
                + msg[user] + '</a></strong></p>');
            $('#powertip-' + user).powerTip({placement: 'w', mouseOnToPopup: 'True'});
            $('#powertip-' + user).data('powertip', '<table class="table table-sm text-center text-dark"><tr><td><i class="fas fa-circle" style="font-size: 10px; color: #33aa44"></i></td>' +
                '<td>' + msg[user] + '</td></tr>' +
                '<tr><td><i class="fas fa-futbol"></i></td><td><i class="fas fa-plus-circle"></i></td></tr>' +
                '</table>');
        }

    });


    socket.on('send_message', function (msg) {
        // allow 1px inaccuracy by adding 1
        var isScrolledToBottom = chatbox.scrollHeight - chatbox.clientHeight <= chatbox.scrollTop + 1;

        $('#chatbox').append('<p><strong>' +
            msg['author'] +
            '</strong> <small class="text-secondary">' +
            msg['timestamp'] +
            '</small><br>' +
            msg['message'] + '</p><hr>'
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
                console.log("Tests");
                if (jQuery.isEmptyObject(message_errors)) {
                    console.log("Tets");
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



