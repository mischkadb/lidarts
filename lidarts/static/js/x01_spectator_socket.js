$(document).ready(function() {
    // namespace for the game handling
    namespace = '/game';
    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    var p1_next_turn;
    var p1_id;
    var p2_id;

    var hashid = $('#hash_id').data();
    socket.on('connect', function() {
        socket.emit('init', {hashid: hashid['hashid'] });
    });

    socket.on('closest_to_bull_score', function(msg) {
        $('#closest_to_bull_notification').text('Throw three darts at bull.');
        $('#p1_score').html('');
        $('#p2_score').html('');
        if (msg.p1_score.length == 0){  $('#p1_score').html('-'); }
        if (msg.p2_score.length == 0){  $('#p2_score').html('-'); }
        $.each(msg.p1_score, function( index, value ){
            $('#p1_score').append(' ' + value);
        });
        $.each(msg.p2_score, function( index, value ){
            $('#p2_score').append(' ' + value);
        });
    });

    socket.on('closest_to_bull_draw', function(msg) {
        $('#p1_score').html('');
        $('#p2_score').html('');
        $.each(msg.p1_score, function( index, value ){
            $('#p1_score').append(' ' + value);
        });
        $.each(msg.p2_score, function( index, value ){
            $('#p2_score').append(' ' + value);
        });
        $('#closest_to_bull_notification').text('Draw. Throw again.');
    });

    socket.on('closest_to_bull_completed', function(msg) {
        $('#p1_score').html('');
        $('#p2_score').html('');
        $.each(msg.p1_score, function( index, value ){
            $('#p1_score').append(' ' + value);
        });
        $.each(msg.p2_score, function( index, value ){
            $('#p2_score').append(' ' + value);
        });
        if (msg.p1_won) {
            $('#closest_to_bull_notification').text('Player 1 to throw first. Game on!');
        } else {
            $('#closest_to_bull_notification').text('Player 2 to throw first. Game on!');
        }
        setTimeout(function() {
            $('#closest_to_bull_notification_div').hide();
            socket.emit('init', {hashid: hashid['hashid'] });
        }, 3000);

    });


    socket.on('game_shot', function(msg) {
        $('#p1_current_leg').text('');

        // display old scores for a short time
        var p1_last_leg_sum = 0;
        if (msg.p1_last_leg.length > 0) {
            p1_last_leg_sum = msg.p1_last_leg.reduce(function(acc, val) {return acc + val})
        }
        // display all single scores for player 1
        $.each(msg.p1_last_leg, function( index, value ){
            // fade in latest score
            if ( index == msg.p1_last_leg.length-1 && p1_last_leg_sum == msg.type) {
                $('#p1_current_leg').prepend(
                    '<div id="new_score_fadein">' +
                    '<div class="row text-light d-flex align-items-center"><div class="col-2"></div>' +
                    '<div class="col-8 text-center"><h2 style="font-weight: bold">' + value + '</h2></div>' +
                    '<div class="col-2 text-right text-secondary"><h3>' + (index+1) + "</h3></div></div></div>"
                );
                $('#new_score_fadein').hide().fadeIn(2000);
            } else {
                $('#p1_current_leg').prepend(
                    '<div class="row text-light d-flex align-items-center"><div class="col-2"></div>' +
                    '<div class="col-8 text-center"><h2 style="font-weight: bold">' + value + '</h2></div>' +
                    '<div class="col-2 text-right text-secondary"><h3>' + (index+1) + "</h3></div></div>"
                )
            };
        });
        // display all single scores for player 2
        $('#p2_current_leg').text('');
        $.each(msg.p2_last_leg, function( index, value ){
            // fade in latest score
            if ( index == msg.p2_last_leg.length-1 && p1_last_leg_sum != msg.type) {
                $('#p2_current_leg').prepend(
                    '<div id="new_score_fadein">' +
                    '<div class="row text-light d-flex align-items-center"><div class="col-2 text-left text-secondary"><h3>' + (index + 1) + '</h3></div>' +
                    '<div class="col-8 text-center"><h2 style="font-weight: bold">' + value + '</h2></div>' +
                    '<div class="col-2"></div></div></div>'
                );
                $('#new_score_fadein').hide().fadeIn(2000);
            } else {
                $('#p2_current_leg').prepend(
                    '<div class="row text-light d-flex align-items-center"><div class="col-2 text-left text-secondary"><h3>' + (index + 1) + '</h3></div>' +
                    '<div class="col-8 text-center"><h2 style="font-weight: bold">' + value + '</h2></div>' +
                    '<div class="col-2"></div></div></div>'
                )
            }
        });

        // show current leg and set scores
        $('.p1_sets').text(msg.p1_sets);
        $('.p2_sets').text(msg.p2_sets);
        $('.p1_legs').text(msg.p1_legs);
        $('.p2_legs').text(msg.p2_legs);

        // popup for game shot
        $('#game-shot-modal').modal('show');
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
                    $('.p1_score').text(Math.ceil(this.Counter));
                }
            }).promise().done(function() {
                setTimeout(function() {
                    $('#game-shot-modal').modal('hide');
                }, 1500);
                // move on after 3 seconds
                setTimeout(function() {
                    socket.emit('get_score_after_leg_win', {hashid: hashid['hashid'] });
                }, 3000);
            });
        } else {
            $('.p1_score').html(msg.p1_score);
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
                    $('.p2_score').text(Math.ceil(this.Counter));
                }
            }).promise().done(function() {
                setTimeout(function() {
                    $('#game-shot-modal').modal('hide');
                }, 1500);
                // move on after 3 seconds
                setTimeout(function() {
                    socket.emit('get_score_after_leg_win', {hashid: hashid['hashid'] });
                }, 3000);
            });
        } else {
            $('.p2_score').text(msg.p2_score);
        }

    });

    // Event handler for server sent score data
    socket.on('score_response', function(msg) {
        p1_next_turn = msg.p1_next_turn;
        p1_id = msg.p1_id;
        p2_id = msg.p2_id;

        if ( !msg.p1_next_turn && msg.old_score > msg.p1_score) {
            // score substraction animation
            jQuery({Counter: msg.old_score}).animate({Counter: msg.p1_score-1}, {
                duration: 1000,
                easing: 'swing',
                step: function () {
                    $('.p1_score').text(Math.ceil(this.Counter));
                }
            });
        } else {
            $('.p1_score').html(msg.p1_score);
        }
        if ( msg.p1_next_turn && msg.old_score > msg.p2_score) {
            // score substraction animation
            jQuery({Counter: msg.old_score}).animate({Counter: msg.p2_score-1}, {
                duration: 1000,
                easing: 'swing',
                step: function () {
                    $('.p2_score').text(Math.ceil(this.Counter));
                }
            });
        } else {
            $('.p2_score').text(msg.p2_score);
        }

        // show current leg and set scores
        $('.p1_sets').text(msg.p1_sets);
        $('.p2_sets').text(msg.p2_sets);
        $('.p1_legs').text(msg.p1_legs);
        $('.p2_legs').text(msg.p2_legs);

        // statistics
        $('.p1_leg_avg').text(msg.p1_leg_avg);
        $('.p2_leg_avg').text(msg.p2_leg_avg);
        $('.p1_match_avg').text(msg.p1_match_avg);
        $('.p2_match_avg').text(msg.p2_match_avg);
        $('.p1_first9_avg').text(msg.p1_first9_avg);
        $('.p2_first9_avg').text(msg.p2_first9_avg);
        $('.p1_100').text(msg.p1_100);
        $('.p2_100').text(msg.p2_100);
        $('.p1_140').text(msg.p1_140);
        $('.p2_140').text(msg.p2_140);
        $('.p1_180').text(msg.p1_180);
        $('.p2_180').text(msg.p2_180);
        $('.p1_doubles').text(msg.p1_doubles);
        $('.p2_doubles').text(msg.p2_doubles);
        $('.p1_high_finish').text(msg.p1_high_finish);
        $('.p2_high_finish').text(msg.p2_high_finish);
        $('.p1_short_leg').text(msg.p1_short_leg);
        $('.p2_short_leg').text(msg.p2_short_leg);
        $('.p1_doubles').text(msg.p1_doubles + '% ('+ msg.p1_legs_won + '/' + msg.p1_darts_thrown_double + ')');
        $('.p2_doubles').text(msg.p2_doubles + '% ('+ msg.p2_legs_won + '/' + msg.p2_darts_thrown_double + ')');

        $('#p1_current_leg').text('');
        $.each(msg.p1_current_leg, function( index, value ){
            if ( index == msg.p1_current_leg.length-1 && !msg.p1_next_turn) {
                $('#p1_current_leg').prepend(
                    '<div id="new_score_fadein">' +
                    '<div class="row text-light d-flex align-items-center"><div class="col-2"></div>' +
                    '<div class="col-8 text-center"><h2 style="font-weight: bold">' + value + '</h2></div>' +
                    '<div class="col-2 text-right text-secondary"><h3>' + (index+1) + "</h3></div></div></div>"
                );
                $('#new_score_fadein').hide().fadeIn(2000);
            } else {
                $('#p1_current_leg').prepend(
                    '<div class="row text-light d-flex align-items-center"><div class="col-2"></div>' +
                    '<div class="col-8 text-center"><h2 style="font-weight: bold">' + value + '</h2></div>' +
                    '<div class="col-2 text-right text-secondary"><h3>' + (index+1) + "</h3></div></div>"
                )
            };
        });
        $('#p2_current_leg').text('');
        $.each(msg.p2_current_leg, function( index, value ){
            if ( index == msg.p2_current_leg.length-1 && msg.p1_next_turn) {
                $('#p2_current_leg').prepend(
                    '<div id="new_score_fadein">' +
                    '<div class="row text-light d-flex align-items-center"><div class="col-2 text-left text-secondary"><h3>' + (index + 1) + '</h3></div>' +
                    '<div class="col-8 text-center"><h2 style="font-weight: bold">' + value + '</h2></div>' +
                    '<div class="col-2"></div></div></div>'
                );
                $('#new_score_fadein').hide().fadeIn(2000);
            } else {
                $('#p2_current_leg').prepend(
                    '<div class="row text-light d-flex align-items-center"><div class="col-2 text-left text-secondary"><h3>' + (index + 1) + '</h3></div>' +
                    '<div class="col-8 text-center"><h2 style="font-weight: bold">' + value + '</h2></div>' +
                    '<div class="col-2"></div></div></div>'
                )
            }
        });

        // Colored turn indicators.
        if (msg.p1_next_turn) {
            $('.p1_turn_outer_card').removeClass('border-0');
            $('.p1_turn_outer_card').addClass('border-1 border-light');
            $('.p1_turn_name_card').removeClass('bg-dark border-0');
            $('.p1_turn_name_card').addClass('bg-secondary');
            $('.p1_turn_score_card').removeClass('bg-secondary');
            $('.p1_turn_score_card').addClass('bg-danger');
            $('.p2_turn_outer_card').removeClass('border-1 border-light');
            $('.p2_turn_outer_card').addClass('border-0');
            $('.p2_turn_name_card').removeClass('bg-secondary');
            $('.p2_turn_name_card').addClass('bg-dark border-0');
            $('.p2_turn_score_card').removeClass('bg-danger');
            $('.p2_turn_score_card').addClass('bg-secondary');

            $('.p1_turn_incidator').html('<i class="fas fa-angle-left"></i>');
            $('.p2_turn_incidator').html('');
        } else {
            $('.p1_turn_outer_card').removeClass('border-1 border-light');
            $('.p1_turn_outer_card').addClass('border-0');
            $('.p1_turn_name_card').removeClass('bg-secondary');
            $('.p1_turn_name_card').addClass('bg-dark border-0');
            $('.p1_turn_score_card').removeClass('bg-danger');
            $('.p1_turn_score_card').addClass('bg-secondary');
            $('.p2_turn_outer_card').removeClass('border-0');
            $('.p2_turn_outer_card').addClass('border-1 border-light');
            $('.p2_turn_name_card').removeClass('bg-dark border-0');
            $('.p2_turn_name_card').addClass('bg-secondary');
            $('.p2_turn_score_card').removeClass('bg-secondary');
            $('.p2_turn_score_card').addClass('bg-danger');

            $('.p1_turn_incidator').html('');
            $('.p2_turn_incidator').html('<i class="fas fa-angle-left"></i>');
        }

    });
    // Remove turn indicators when game is over and show link to game overview
    socket.on('game_completed', function(msg) {
        $('#p1_current_leg').text('');
        var p1_last_leg_sum = 0;
        if (msg.p1_last_leg.length > 0) {
            p1_last_leg_sum = msg.p1_last_leg.reduce(function(acc, val) {return acc + val})
        }
        $.each(msg.p1_last_leg, function( index, value ){
            if ( index == msg.p1_last_leg.length-1 && p1_last_leg_sum == msg.type) {
                $('#p1_current_leg').prepend(
                    '<div id="new_score_fadein">' +
                    '<div class="row text-light d-flex align-items-center"><div class="col-2"></div>' +
                    '<div class="col-8 text-center"><h2 style="font-weight: bold">' + value + '</h2></div>' +
                    '<div class="col-2 text-right text-secondary"><h3>' + (index+1) + "</h3></div></div></div>"
                );
                $('#new_score_fadein').hide().fadeIn(2000);
            } else {
                $('#p1_current_leg').prepend(
                    '<div class="row text-light d-flex align-items-center"><div class="col-2"></div>' +
                    '<div class="col-8 text-center"><h2 style="font-weight: bold">' + value + '</h2></div>' +
                    '<div class="col-2 text-right text-secondary"><h3>' + (index+1) + "</h3></div></div>"
                )
            };
        });
        $('#p2_current_leg').text('');
        $.each(msg.p2_last_leg, function( index, value ){
            if ( index == msg.p2_last_leg.length-1 && p1_last_leg_sum != msg.type) {
                $('#p2_current_leg').prepend(
                    '<div id="new_score_fadein">' +
                    '<div class="row text-light d-flex align-items-center"><div class="col-2 text-left text-secondary"><h3>' + (index + 1) + '</h3></div>' +
                    '<div class="col-8 text-center"><h2 style="font-weight: bold">' + value + '</h2></div>' +
                    '<div class="col-2"></div></div></div>'
                );
                $('#new_score_fadein').hide().fadeIn(2000);
            } else {
                $('#p2_current_leg').prepend(
                    '<div class="row text-light d-flex align-items-center"><div class="col-2 text-left text-secondary"><h3>' + (index + 1) + '</h3></div>' +
                    '<div class="col-8 text-center"><h2 style="font-weight: bold">' + value + '</h2></div>' +
                    '<div class="col-2"></div></div></div>'
                )
            }
        });

        $('.p1_sets').text(msg.p1_sets);
        $('.p2_sets').text(msg.p2_sets);
        $('.p1_legs').text(msg.p1_legs);
        $('.p2_legs').text(msg.p2_legs);

        $('#match-shot-modal').modal('show');
        if (msg.p1_won) {
            jQuery({Counter: msg.p1_last_leg[msg.p1_last_leg.length-1]}).animate({Counter: -1}, {
                duration: 1000,
                easing: 'swing',
                step: function () {
                    $('.p1_score').text(Math.ceil(this.Counter));
                }
            }).promise().done(function() {
                setTimeout(function() {
                    $('#match-shot-modal').modal('hide');
                }, 1500);
            });
        } else {
            $('.p1_score').html(msg.p1_score);
        }
        if (!msg.p1_won) {
            jQuery({Counter: msg.p2_last_leg[msg.p2_last_leg.length-1]}).animate({Counter: -1}, {
                duration: 1000,
                easing: 'swing',
                step: function () {
                    $('.p2_score').text(Math.ceil(this.Counter));
                }
            }).promise().done(function() {
                setTimeout(function() {
                    $('#match-shot-modal').modal('hide');
                }, 1500);
            });
        } else {
            $('.p2_score').html(msg.p2_score);
        }
        $('.score_input').hide();
        $('.confirm_completion').show();
    });



});

