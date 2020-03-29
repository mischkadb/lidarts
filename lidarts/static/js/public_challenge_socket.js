$(document).ready(function() {
    // namespace for the game handling
    namespace = '/public_challenge';
    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace, {transports: ['websocket']});
    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    var username = $('#user_name').data()['username'];
    console.log(username);

    socket.on('broadcast_public_challenges', function(msg) {
        $('#public_challenge_list').text('');
        if (msg['public_challenges'].length == 0) {
            $('#public_challenge_list').html('<center>------</center>');
        } 

        for(i in msg['public_challenges']) {
            public_challenge = msg['public_challenges'][i]

            if (public_challenge['username'] == username){
                continue;
            }

            if (public_challenge['two_clear_legs'] == true) {
                two_clear_legs = ' | Two clear legs'
            } else {
                two_clear_legs = ''
            }

            if (public_challenge['closest_to_bull'] == true) {
                closest_to_bull = ' | Closest to bull begins'
            } else {
                closest_to_bull = ''
            }

            if (public_challenge['bo_sets'] > 1) {
                bo_sets = ' | bo' + public_challenge['bo_sets'] + ' sets'
            } else {
                bo_sets = ''
            }
            
            $('#public_challenge_list').append(
                '<p><a href="game/' + public_challenge['hashid'] + '" class="text-dark mt-2"><strong>' + public_challenge['username'] + '</strong> | '
                + 'Avg.: ' + public_challenge['average'] + '<br>'
                + public_challenge['type'] + ' ' +  public_challenge['in_mode'] + '/' +  public_challenge['out_mode'] + ' | '
                + 'bo' + public_challenge['bo_legs'] + ' legs'
                + bo_sets
                + two_clear_legs
                + closest_to_bull
                + '</a></p>'
                + '<hr>'
            );
        }
        
    });

});