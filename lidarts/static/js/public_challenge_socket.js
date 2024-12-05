$(document).ready(function () {
    // namespace for the game handling
    namespace = '/public_challenge';
    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace, { transports: ['websocket'] });
    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    var username = $('#user_name').data()['username'];
    var game_url = $('#game_url').data()['url'];
    console.log(username);

    socket.on('broadcast_public_challenges', function (msg) {
        $('#public_challenge_list').text('');
        if (msg['public_challenges'].length == 0) {
            $('#public_challenge_list').html('<center>------</center>');
        }

        for (i in msg['public_challenges']) {
            public_challenge = msg['public_challenges'][i]

            if (public_challenge['username'] == username) {
                continue;
            }

            if (public_challenge['two_clear_legs'] == true) {
                two_clear_legs = ' | Two clear legs'
            } else {
                two_clear_legs = ''
            }

            if (public_challenge['two_clear_legs_wc_mode'] == true) {
                two_clear_legs_wc_mode = ' | World Champ. mode'
            } else {
                two_clear_legs_wc_mode = ''
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

            bo_legs = 'bo' + public_challenge['bo_legs'] + ' legs'

            if (public_challenge['goal_mode'] == 'x_legs') {
                x_legs = ' | ' + public_challenge['x_legs'] + ' legs'
                bo_sets = ''
                bo_legs = ''
            } else {
                x_legs = ''
            }

            if (public_challenge['score_input_delay'] > 0) {
                score_input_delay = ' | Input block: ' + public_challenge['score_input_delay'] + 's'
            } else {
                score_input_delay = ''
            }

            if (public_challenge['webcam']) {
                webcam = ' | Webcam'
            } else {
                webcam = ''
            }

            if (public_challenge['variant'] == 'x01') {
                type = public_challenge['type'] + ' ';
                mode = public_challenge['in_mode'] + '/' + public_challenge['out_mode'] + ' | '
            } else {
                type = 'Cricket ';
                mode = '';
            }


            $('#public_challenge_list').append(
                '<p><a href="' + game_url + public_challenge['hashid'] + '" class="text-dark mt-2"><strong>' + public_challenge['username'] + '</strong> | '
                + 'Avg.: ' + public_challenge['average'] + '<br>'
                + type
                + mode
                + bo_legs
                + bo_sets
                + x_legs
                + two_clear_legs
                + two_clear_legs_wc_mode
                + closest_to_bull
                + score_input_delay
                + webcam
                + '</a></p>'
                + '<hr>'
            );
        }

    });

});