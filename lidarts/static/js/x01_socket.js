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
    var hashid = $('#hash_id').data();
    socket.on('connect', function() {
        socket.emit('init', {hashid: hashid['hashid'] });
    });
    socket.on('game_shot', function(msg) {
        $('#game-shot-modal').modal('show');
        if (msg.p1_won) {
            var last_score = msg.type;
            for (var i = 0; i < msg.p1_last_leg.length-1; i++) {
                last_score -= msg.p1_last_leg[i] << 0;
            }
            jQuery({Counter: last_score}).animate({Counter: -1}, {
                duration: 1000,
                easing: 'swing',
                step: function () {
                    $('#p1_score').text(Math.ceil(this.Counter));
                }
            }).promise().done(function() {
                    setTimeout(function() {
                     $('#game-shot-modal').modal('hide');
                    }, 1500);
                    setTimeout(function() {
                     socket.emit('get_score_after_leg_win', {hashid: hashid['hashid'] });
                    }, 3000);
                });
        } else {
            $('#p1_score').html(msg.p1_score);
        }
        if (!msg.p1_won) {
            var last_score = msg.type;
            for (var i = 0; i < msg.p2_last_leg.length-1; i++) {
                last_score -= msg.p2_last_leg[i] << 0;
            }
            jQuery({Counter: last_score}).animate({Counter: -1}, {
                duration: 1500,
                easing: 'swing',
                step: function () {
                    $('#p2_score').text(Math.ceil(this.Counter));
                }
            }).promise().done(function() {
                    setTimeout(function() {
                     $('#game-shot-modal').modal('hide');
                    }, 1500);
                    setTimeout(function() {
                     socket.emit('get_score_after_leg_win', {hashid: hashid['hashid'] });
                    }, 3000);
                });
        } else {
            $('#p2_score').html(msg.p2_score);
        }

    });

    // Event handler for server sent score data
    socket.on('score_response', function(msg) {
        if ( !msg.p1_next_turn && msg.old_score > msg.p1_score) {
            jQuery({Counter: msg.old_score}).animate({Counter: msg.p1_score-1}, {
                duration: 1000,
                easing: 'swing',
                step: function () {
                    $('#p1_score').text(Math.ceil(this.Counter));
                }
            });
        } else {
            $('#p1_score').html(msg.p1_score);
        }
        if ( msg.p1_next_turn && msg.old_score > msg.p2_score) {
            jQuery({Counter: msg.old_score}).animate({Counter: msg.p2_score-1}, {
                duration: 1000,
                easing: 'swing',
                step: function () {
                    $('#p2_score').text(Math.ceil(this.Counter));
                }
            });
        } else {
            $('#p2_score').html(msg.p2_score);
        }
        $('#p1_sets').html(msg.p1_sets);
        $('#p2_sets').html(msg.p2_sets);
        $('#p1_legs').html(msg.p1_legs);
        $('#p2_legs').html(msg.p2_legs);
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
            $('#p1_turn_outer_card').removeClass('bg-dark border-0');
            $('#p1_turn_outer_card').addClass('bg-dark border-1 border-light');
            $('#p1_turn_name_card').removeClass('bg-dark border-0');
            $('#p1_turn_name_card').addClass('bg-secondary');
            $('#p1_turn_score_card').removeClass('bg-secondary');
            $('#p1_turn_score_card').addClass('bg-danger');
            $('#p2_turn_outer_card').removeClass('bg-secondary text-light');
            $('#p2_turn_outer_card').addClass('bg-dark border-0');
            $('#p2_turn_name_card').removeClass('bg-secondary');
            $('#p2_turn_name_card').addClass('bg-dark border-0');
            $('#p2_turn_score_card').removeClass('bg-danger');
            $('#p2_turn_score_card').addClass('bg-secondary');
        } else {
            $('#p1_turn_outer_card').removeClass('bg-secondary text-light');
            $('#p1_turn_outer_card').addClass('bg-dark border-0');
            $('#p1_turn_name_card').removeClass('bg-secondary');
            $('#p1_turn_name_card').addClass('bg-dark border-0');
            $('#p1_turn_score_card').removeClass('bg-danger');
            $('#p1_turn_score_card').addClass('bg-secondary');
            $('#p2_turn_outer_card').removeClass('bg-dark border-0');
            $('#p2_turn_outer_card').addClass('bg-dark border-1 border-light');
            $('#p2_turn_name_card').removeClass('bg-dark border-0');
            $('#p2_turn_name_card').addClass('bg-secondary');
            $('#p2_turn_score_card').removeClass('bg-secondary');
            $('#p2_turn_score_card').addClass('bg-danger');
        }
    });
    // Remove turn indicators when game is over and show link to game overview
    socket.on('game_completed', function(msg) {
        $('#match-shot-modal').modal('show');
        if (msg.p1_won) {
            jQuery({Counter: msg.p1_last_leg[msg.p1_last_leg.length-2]}).animate({Counter: -1}, {
                duration: 1000,
                easing: 'swing',
                step: function () {
                    $('#p1_score').text(Math.ceil(this.Counter));
                }
            }).promise().done(function() {
                    setTimeout(function() {
                     $('#match-shot-modal').modal('hide');
                    }, 1500);
                });
        } else {
            $('#p1_score').html(msg.p1_score);
        }
        if (!msg.p1_won) {
            jQuery({Counter: msg.p2_last_leg[msg.p2_last_leg.length-2]}).animate({Counter: -1}, {
                duration: 1500,
                easing: 'swing',
                step: function () {
                    $('#p2_score').text(Math.ceil(this.Counter));
                }
            }).promise().done(function() {
                    setTimeout(function() {
                     $('#match-shot-modal').modal('hide');
                    }, 1500);
                });
        } else {
            $('#p2_score').html(msg.p2_score);
        }
        $('#score_input').hide();
        $('#confirm_completion').show();
    });
    // Handler for the score input form.
    var validation_url = $('#validation_url').data();
    var user_id = $('#user_id').data();
    var score_errors = [];
    $('form#score_input').submit(function(event) {
        $('#score_error').text('');
        $.post(
            // Various errors that are caught if you enter something wrong.
            validation_url,
            $("#score_input").serialize(),
            function (errors) {
                score_errors = errors
                if (jQuery.isEmptyObject(score_errors)) {
                    socket.emit('send_score', {score: $('#score_value').val(), hashid: hashid['hashid'],
                    user_id: user_id['id']});
                } else {
                    $('#score_error').text(score_errors['score_value'][0]);
                }
                $('input[name=score_value]').val('');
            });
        return false;
    });



});

$(document).keypress(function(e){
    var keyCode = e.which;

    var score_input = document.getElementById('score_value');


    if (document.activeElement != score_input) {
        // 1
        if (keyCode == 49 || keyCode == 97) {
            $('#score_value').val($('#score_value').val() + '1');
        }
        // 2
        else if (keyCode == 50 || keyCode == 98) {
            $('#score_value').val($('#score_value').val() + '2');
        }
        // 3
        else if (keyCode == 51 || keyCode == 99) {
            $('#score_value').val($('#score_value').val() + '3');
        }
        // 4
        else if (keyCode == 52 || keyCode == 100) {
            $('#score_value').val($('#score_value').val() + '4');
        }
        // 5
        else if (keyCode == 53 || keyCode == 101) {
            $('#score_value').val($('#score_value').val() + '5');
        }
        // 6
        else if (keyCode == 54 || keyCode == 102) {
            $('#score_value').val($('#score_value').val() + '6');
        }
        // 7
        else if (keyCode == 55 || keyCode == 103) {
            $('#score_value').val($('#score_value').val() + '7');
        }
        // 8
        else if (keyCode == 56 || keyCode == 104) {
            $('#score_value').val($('#score_value').val() + '8');
        }
        // 9
        else if (keyCode == 57 || keyCode == 105) {
            $('#score_value').val($('#score_value').val() + '9');
        }
        // 0
        else if (keyCode == 48 || keyCode == 96) {
            $('#score_value').val($('#score_value').val() + '0');
        }
        else if (keyCode == 13) {
            $('form#score_input').submit();
        }
    }
});

$('#button-1').click(function() {
        $('#score_value').val($('#score_value').val() + '1');
    })
$('#button-2').click(function() {
        $('#score_value').val($('#score_value').val() + '2');
    })
$('#button-3').click(function() {
        $('#score_value').val($('#score_value').val() + '3');
    })
$('#button-4').click(function() {
        $('#score_value').val($('#score_value').val() + '4');
    })
$('#button-5').click(function() {
        $('#score_value').val($('#score_value').val() + '5');
    })
$('#button-6').click(function() {
        $('#score_value').val($('#score_value').val() + '6');
    })
$('#button-7').click(function() {
        $('#score_value').val($('#score_value').val() + '7');
    })
$('#button-8').click(function() {
        $('#score_value').val($('#score_value').val() + '8');
    })
$('#button-9').click(function() {
        $('#score_value').val($('#score_value').val() + '9');
    })
$('#button-0').click(function() {
        $('#score_value').val($('#score_value').val() + '0');
    })
$('#button-del').click(function() {
        $('#score_value').val('');
    })
$('#button-conf').click(function() {
        $('form#score_input').submit();
    })

$('#hide-keypad').click(function() {
        $('#input-keypad').toggle();
    })
