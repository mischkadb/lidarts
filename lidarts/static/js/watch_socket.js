$(document).ready(function() {
    // namespace for the game handling
    namespace = '/game';
    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace, {transports: ['websocket']});
    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    var hashids = [];

    for (var i = 0; i <= 26; i++){
       if($("#hash_id-" + (i+1)).length > 0) {
           hashids[i] = $('#hash_id-' + (i+1)).data()['hashid'];
       }
    }

    socket.on('connect', function() {
        for (var i = 0; i < hashids.length; i++) {
            socket.emit('init', {hashid: hashids[i] });
        }

    });

    socket.on('game_shot', function(msg) {

        // show current leg and set scores
        $('.p1_sets_' + msg.hashid).text(msg.p1_sets);
        $('.p2_sets_' + msg.hashid).text(msg.p2_sets);
        $('.p1_legs_' + msg.hashid).text(msg.p1_legs);
        $('.p2_legs_' + msg.hashid).text(msg.p2_legs);

        // popup for game shot
        if (msg.p1_won) {
            var last_score = msg.type;
            for (var i = 0; i < msg.p1_last_leg.length-1; i++) {
                last_score -= msg.p1_last_leg[i] << 0;
            }
            // score substraction animation
            jQuery({Counter: last_score}).animate({Counter: -1}, {
                duration: 1000,
                easing: 'swing',
                step: function () {
                    $('.p1_score_' + msg.hashid).text(Math.ceil(this.Counter));
                }
            }).promise().done(function() {
                    // move on after 3 seconds
                    setTimeout(function() {
                     socket.emit('get_score_after_leg_win', {hashid: hashid['hashid'] });
                    }, 3000);
                });
        } else {
            $('.p1_score_' + msg.hashid).html(msg.p1_score);
        }
        if (!msg.p1_won) {
            var last_score = msg.type;
            for (var i = 0; i < msg.p2_last_leg.length-1; i++) {
                last_score -= msg.p2_last_leg[i] << 0;
            }
            // score substraction animation
            jQuery({Counter: last_score}).animate({Counter: -1}, {
                duration: 1500,
                easing: 'swing',
                step: function () {
                    $('.p2_score_' + msg.hashid).text(Math.ceil(this.Counter));
                }
            }).promise().done(function() {
                    // move on after 3 seconds
                    setTimeout(function() {
                     socket.emit('get_score_after_leg_win', {hashid: hashid['hashid'] });
                    }, 3000);
                });
        } else {
            $('.p2_score_' + msg.hashid).text(msg.p2_score);
        }

    });

    // Event handler for server sent score data
    socket.on('score_response', function(msg) {
        if ( !msg.p1_next_turn && msg.old_score > msg.p1_score) {
            // score substraction animation
            jQuery({Counter: msg.old_score}).animate({Counter: msg.p1_score-1}, {
                duration: 1000,
                easing: 'swing',
                step: function () {
                    $('.p1_score_' + msg.hashid).text(Math.ceil(this.Counter));
                }
            });
        } else {
            $('.p1_score_' + msg.hashid).html(msg.p1_score);
        }
        if ( msg.p1_next_turn && msg.old_score > msg.p2_score) {
            // score substraction animation
            jQuery({Counter: msg.old_score}).animate({Counter: msg.p2_score-1}, {
                duration: 1000,
                easing: 'swing',
                step: function () {
                    $('.p2_score_' + msg.hashid).text(Math.ceil(this.Counter));
                }
            });
        } else {
            $('.p2_score_' + msg.hashid).text(msg.p2_score);
        }

        // show current leg and set scores
        $('.p1_sets_' + msg.hashid).text(msg.p1_sets);
        $('.p2_sets_' + msg.hashid).text(msg.p2_sets);
        $('.p1_legs_' + msg.hashid).text(msg.p1_legs);
        $('.p2_legs_' + msg.hashid).text(msg.p2_legs);

        // statistics
        $('.p1_match_avg_' + msg.hashid).text(msg.p1_match_avg);
        $('.p2_match_avg_' + msg.hashid).text(msg.p2_match_avg);
        $('.p1_first9_avg_' + msg.hashid).text(msg.p1_first9_avg);
        $('.p2_first9_avg_' + msg.hashid).text(msg.p2_first9_avg);
        $('.p1_doubles_' + msg.hashid).text(msg.p1_doubles);
        $('.p2_doubles_' + msg.hashid).text(msg.p2_doubles);

        // Colored turn indicators.
        if (msg.p1_next_turn) {

            $('.p1_turn_incidator_' + msg.hashid).html('<i class="fas fa-angle-left"></i>');
            $('.p2_turn_incidator_' + msg.hashid).html('');
        } else {
            $('.p1_turn_incidator_' + msg.hashid).html('');
            $('.p2_turn_incidator_' + msg.hashid).html('<i class="fas fa-angle-left"></i>');
        }
    });

    // Remove turn indicators when game is over and show link to game overview
    socket.on('game_completed', function(msg) {
        $('.p1_sets_' + msg.hashid).text(msg.p1_sets);
        $('.p2_sets_' + msg.hashid).text(msg.p2_sets);
        $('.p1_legs_' + msg.hashid).text(msg.p1_legs);
        $('.p2_legs_' + msg.hashid).text(msg.p2_legs);

        if (msg.p1_won) {
            jQuery({Counter: msg.p1_last_leg[msg.p1_last_leg.length-1]}).animate({Counter: -1}, {
                duration: 1000,
                easing: 'swing',
                step: function () {
                    $('.p1_score_' + msg.hashid).text(Math.ceil(this.Counter));
                }
            });
        } else {
            $('.p1_score_' + msg.hashid).html(msg.p1_score);
        }
        if (!msg.p1_won) {
            jQuery({Counter: msg.p2_last_leg[msg.p2_last_leg.length-1]}).animate({Counter: -1}, {
                duration: 1000,
                easing: 'swing',
                step: function () {
                    $('.p2_score_' + msg.hashid).text(Math.ceil(this.Counter));
                }
            });
        } else {
            $('.p2_score_' + msg.hashid).html(msg.p2_score);
        }
    });


});

