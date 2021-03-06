$(document).ready(function() {

    // Scroll chatbox to bottom (latest message)
    var chatbox = document.getElementById("chatbox");
    chatbox.scrollTop = chatbox.scrollHeight;

    // namespace for handling
    namespace = '/game_chat';

    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace, {transports: ['websocket']});

    var cdn_url = '';
    
    if (window.location.hostname == 'lidarts.org') {
        cdn_url = 'https://lidartsstatic.org'
    }

    var user_id = $('#user_id').data()['id'];
    var hashid = $('#hash_id').data();

    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    socket.on('connect', function() {
        socket.emit('init', {hashid: hashid['hashid'] });
    });


    socket.on('send_message', function (msg) {
    console.log('received');
        // allow 1px inaccuracy by adding 1
        var isScrolledToBottom = chatbox.scrollHeight - chatbox.clientHeight <= chatbox.scrollTop + 1;

        $('.chatbox').append('<p><strong>' + msg['author'] + '</strong>: ' + msg['message'] + '</p>');

        if(isScrolledToBottom)
            chatbox.scrollTop = chatbox.scrollHeight - chatbox.clientHeight;

        if (user_id != msg['author_id']) {
            var audio = new Audio(cdn_url + '/static/sounds/notification.mp3');
            audio.play();
        }
    });


    var waiting_for_ack = false;
    $('form#message_input').submit(function (event) {
        event.preventDefault(); 
        if (waiting_for_ack == true || $('#message').val().length == 0) {
            return;
        }
        waiting_for_ack = true;
        socket.emit(
            'broadcast_game_chat_message',
            {message: $('#message').val(), user_id: user_id, hash_id: hashid['hashid']},
            function () {
                $('input[name=message]').val('');
                waiting_for_ack = false;
            }
        );       
    });

    $('form#message_input_small').submit(function (event) {
        event.preventDefault(); 
        if (waiting_for_ack == true || $('#message_small').val().length == 0) {
            return;
        }
        waiting_for_ack = true;
        socket.emit(
            'broadcast_game_chat_message',
            {message: $('#message_small').val(), user_id: user_id, hash_id: hashid['hashid']},
            function () {
                $('input[name=message]').val('');
                waiting_for_ack = false;
            }
        );       
    });

});



