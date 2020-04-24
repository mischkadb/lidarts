$(document).ready(function() {
    // namespace for the game handling
    namespace = '/game/cricket';
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

    var game_completed = false;
    var game_url = $('#game_url').data()['url'];
    var caller = $('#caller').data()['caller'];

    var hashid = $('#hash_id').data();
    socket.on('connect', function() {
        socket.emit('init', {hashid: hashid['hashid'] });
    });

    var muted = false;

    socket.emit('player_heartbeat', {hashid: hashid['hashid']});

    window.setInterval(function(){
        /// call your function here
        socket.emit('player_heartbeat', {hashid: hashid['hashid']});
    }, 5000);

    socket.on('game_aborted', function(msg) {
        $('.score_input').hide();
        $('.game-aborted').show();
    });

    socket.on('players_ingame', function(msg) {
        if (msg.p1_ingame === true) {
            $('#p1_ingame').hide();
        } else {
            $('#p1_ingame').show();
        }
        if (msg.p2_ingame === true) {
            $('#p2_ingame').hide();
        } else {
            $('#p2_ingame').show();
        }
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

    function update_scoreboards(msg) {
        // show current leg and set scores
        $('.p1_sets').text(msg.p1_sets);
        $('.p2_sets').text(msg.p2_sets);
        $('.p1_legs').text(msg.p1_legs);
        $('.p2_legs').text(msg.p2_legs);

        // statistics
        $('.p1_leg_mpr').text(msg.p1_leg_mpr);
        $('.p2_leg_mpr').text(msg.p2_leg_mpr);
        $('.p1_match_mpr').text(msg.p1_match_mpr);
        $('.p2_match_mpr').text(msg.p2_match_mpr);

        var score_display = {
            0: '0',
            15: 'S15',
            16: 'S16',
            17: 'S17',
            18: 'S18',
            19: 'S19',
            20: 'S20',
            25: 'S25',
            30: 'D15',
            32: 'D16',
            34: 'D17',
            36: 'D18',
            38: 'D19',
            40: 'D20',
            50: 'D25',
            45: 'T15',
            48: 'T16',
            51: 'T17',
            54: 'T18',
            57: 'T19',
            60: 'T20',
        }

        if (msg.p1_current_leg.length > 0) {
            $('#p1_last_round').text('');
            if (!(msg.score_confirmed && msg.p1_next_turn)) {
                msg.p1_current_leg[msg.p1_current_leg.length - 1].forEach(function(score, index) {
                    $('#p1_last_round').append(score_display[score] + ' ');
                });
            }
        } else {
            $('#p1_last_round').text('');
        }

        if (msg.p2_current_leg.length > 0) {
            $('#p2_last_round').text('');
            if (!(msg.score_confirmed && !msg.p1_next_turn)) {
                msg.p2_current_leg[msg.p2_current_leg.length - 1].forEach(function(score, index) {
                    $('#p2_last_round').append(score_display[score] + ' ');
                });
            }
        } else {
            $('#p2_last_round').text('');
        }

        $.each(msg.p1_current_fields, function(index, value){
            for (i = 1; i <= 3; i++) {
                if (value['score'] > 0) {
                    $('#marks-p1-' + index + '-score').text(value['score']);
                } else {
                    $('#marks-p1-' + index + '-score').text('');
                }

                if (value['marks'] >= i) {
                    $('#marks-p1-' + index + '-' + i).show();
                } else {
                    $('#marks-p1-' + index + '-' + i).hide();
                }
                
                if (value['marks'] == 3 && msg.p2_current_fields[index]['marks'] == 3) {
                    $('#score-button-S' + index).addClass('disabled');
                    $('#score-button-D' + index).addClass('disabled');
                    if (index < 25) {
                        $('#score-button-T' + index).addClass('disabled');
                    }                    
                } else {
                    $('#score-button-S' + index).removeClass('disabled');
                    $('#score-button-D' + index).removeClass('disabled');
                    if (index < 25) {
                        $('#score-button-T' + index).removeClass('disabled');
                    }  
                }
            }            
        });

        $.each(msg.p2_current_fields, function(index, value){
            for (i = 1; i <= 3; i++) {
                if (value['score'] > 0) {
                    $('#marks-p2-' + index + '-score').text(value['score']);
                } else {
                    $('#marks-p2-' + index + '-score').text('');
                }

                if (value['marks'] >= i) {
                    $('#marks-p2-' + index + '-' + i).show();
                } else {
                    $('#marks-p2-' + index + '-' + i).hide();
                }
            }            
        });
    }

    socket.on('game_shot', function(msg) {
        if (muted == false) {
            var audio = new Audio('/static/sounds/' + caller + '/game_shot.mp3');
            audio.play();
        }

        update_scoreboards(msg);

        // popup for game shot
        $('#game-shot-modal').modal('show');
        if (msg.p1_won) {
            // score substraction animation
            jQuery({Counter:  msg.p1_old_score}).animate({Counter: msg.p1_last_score-1}, {
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
            $('.p1_score').html(msg.p1_last_score);
        }
        
        if (!msg.p1_won) {
            // score substraction animation
            jQuery({Counter: msg.p2_old_score}).animate({Counter: msg.p2_last_score-1}, {
                duration: 1000,
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
            $('.p2_score').text(msg.p2_last_score);
        }

    });

    // Event handler for server sent score data
    socket.on('score_response', function(msg) {
        p1_next_turn = msg.p1_next_turn;
        p1_id = msg.p1_id;
        p2_id = msg.p2_id;

        var score = 0;

        if ( msg.p1_old_score < msg.p1_score) {
            // score substraction animation
            jQuery({Counter: msg.p1_old_score}).animate({Counter: msg.p1_score-1}, {
                duration: 1000,
                easing: 'swing',
                step: function () {
                    $('.p1_score').text(Math.ceil(this.Counter));
                },
                complete: function () {
                    $('.p1_score').html(msg.p1_score);
                }
            });
        } else {
            $('.p1_score').html(msg.p1_score);
        }
        if ( msg.p2_old_score < msg.p2_score) {
            score = msg.p2_score - msg.p2_old_score;
            // score substraction animation
            jQuery({Counter: msg.p2_old_score}).animate({Counter: msg.p2_score-1}, {
                duration: 1000,
                easing: 'swing',
                step: function () {
                    $('.p2_score').text(Math.ceil(this.Counter));
                },
                complete: function () {
                    $('.p2_score').html(msg.p2_score);
                }
            });
        } else {
            $('.p2_score').text(msg.p2_score);
        }

        update_scoreboards(msg);

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

        if (msg.computer_game && !msg.p1_next_turn) {
            setTimeout(function() {
                socket.emit('send_score', {hashid: hashid['hashid'],
                    user_id: user_id['id'], computer: true});
            }, 2000);

        }
    });
    // Remove turn indicators when game is over and show link to game overview
    socket.on('game_completed', function(msg) {
        if (muted == false){
            var audio = new Audio('/static/sounds/' + caller + '/game_shot_match.mp3');
            audio.play();
        }

        update_scoreboards(msg);

        $('#match-shot-modal').modal('show');
        if (msg.p1_won) {
            // score substraction animation
            jQuery({Counter:  msg.p1_old_score}).animate({Counter: msg.p1_last_score-1}, {
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
            $('.p1_score').html(msg.p1_last_score);
        }
        
        if (!msg.p1_won) {
            // score substraction animation
            jQuery({Counter: msg.p2_old_score}).animate({Counter: msg.p2_last_score-1}, {
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
            $('.p2_score').text(msg.p2_last_score);
        }

        $('.score_input').hide();
        $('.confirm_completion').show();

        game_completed = true
    });

    function confirm_score() {
        socket.emit('confirm_score', {hashid: hashid['hashid']});
    };

    function undo_score() {
        socket.emit('undo_score', {hashid: hashid['hashid']});
    };

    function send_score(score_value){
        socket.emit('send_score', {
            score: score_value, hashid: hashid['hashid'],
            user_id: user_id['id'],
        });

        $('input[name=score_value]').val('');
        $('#score_value_sm').val($('#score_value').val());
    };

    // Handler for the score input form.
    var user_id = $('#user_id').data();

    $('form#score_input').submit(function(event) {
        var score_value = $('#score_value').val();

        // check for valid input values
        if (score_value <= 60) {
            // player 1 handler
            if ((user_id['id'] == p1_id && p1_next_turn) || (p1_id == null)) {
                send_score(score_value);
            }
            // player 2 handler
            else if ((user_id['id'] == p2_id && !p1_next_turn) || (p2_id == null)) {
                send_score(score_value);
            }
            return false;
        } else {
            $('#score_value').val('');
            return false;
        }
    });

    // handle key inputs
    $(document).keydown(function(e){
        var keyCode = e.which;
        var score_input = document.getElementById('score_value');
        var message_input = document.getElementById('message');
        var message_input_small = document.getElementById('message_small');

        if (document.activeElement != score_input
            && document.activeElement != message_input && document.activeElement != message_input_small
            && game_completed == false) {
            // 1
            if (keyCode == 49 || keyCode == 97) {
                $('.score_value').val($('.score_value').val() + '1');
            }
            // 2
            else if (keyCode == 50 || keyCode == 98) {
                $('.score_value').val($('.score_value').val() + '2');
            }
            // 3
            else if (keyCode == 51 || keyCode == 99) {
                $('.score_value').val($('.score_value').val() + '3');
            }
            // 0
            else if (keyCode == 48 || keyCode == 96) {
                $('.score_value').val($('.score_value').val() + '0');
            }
            // 4
            else if (keyCode == 52 || keyCode == 100) {
                $('.score_value').val($('.score_value').val() + '4');
            }
            // 5
            else if (keyCode == 53 || keyCode == 101) {
                $('.score_value').val($('.score_value').val() + '5');
            }
            // 6
            else if (keyCode == 54 || keyCode == 102) {
                $('.score_value').val($('.score_value').val() + '6');
            }
            // 7
            else if (keyCode == 55 || keyCode == 103) {
                $('.score_value').val($('.score_value').val() + '7');
            }
            // 8
            else if (keyCode == 56 || keyCode == 104) {
                $('.score_value').val($('.score_value').val() + '8');
            }
            // 9
            else if (keyCode == 57 || keyCode == 105) {
                $('.score_value').val($('.score_value').val() + '9');
            }
            else if (keyCode == 13) {
                $('.score_input').submit();
            }
            else if (keyCode == 8) {
                e.preventDefault();
                if ($('.score_value').val() == '') {
                    undo_score()
                } else {
                    $('.score_value').val($('.score_value').val().slice(0, -1));
                }
            }
        }
    });
    
    // onscreen keyboard functions
    $('#score-button-0').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(0);
        }        
    });

    $('#score-button-S15').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(15);
        }        
    });

    $('#score-button-D15').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(30);
        }        
    });

    $('#score-button-T15').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(45);
        }        
    });

    $('#score-button-S16').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(16);
        }        
    });

    $('#score-button-D16').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(32);
        }        
    });

    $('#score-button-T16').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(48);
        }        
    });

    $('#score-button-S17').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(17);
        }        
    });

    $('#score-button-D17').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(34);
        }        
    });

    $('#score-button-T17').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(51);
        }        
    });

    $('#score-button-S18').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(18);
        }        
    });

    $('#score-button-D18').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(36);
        }        
    });

    $('#score-button-T18').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(54);
        }        
    });

    $('#score-button-S19').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(19);
        }        
    });

    $('#score-button-D19').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(38);
        }        
    });

    $('#score-button-T19').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(57);
        }        
    });

    $('#score-button-S20').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(20);
        }        
    });

    $('#score-button-D20').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(40);
        }        
    });

    $('#score-button-T20').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(60);
        }        
    });

    $('#score-button-S25').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(25);
        }        
    });

    $('#score-button-D25').click(function() {
        if ($(this).hasClass('disabled') == false) {
            send_score(50);
        }        
    });

    // Toggle keypad
    $('#hide-statistics').click(function() {
        $('.statistics').toggle();
    });

    // Toggle chat
    $('#toggle-chat').click(function() {
        $('#chat').toggle();
        $('#cricket_scoreboard').toggle();
    });

    // Abort game
    $('#abort-game').click(function() {
        $('#abort-game-modal').modal('show');
    });

    $('#mute').click(function() {
        muted = true;
        $('#unmute').show();
        $('#mute').hide();
    });

    $('#unmute').click(function() {
        muted = false;
        $('#mute').show();
        $('#unmute').hide();
    });

    $('#abort-confirm').click(function() {
        var hashid = $('#hash_id').data()['hashid'];
        var abort_url = $('#abort_url').data()['url'];
        $.post(abort_url + hashid);
    });

    $('#score-confirm').click(function() {
        confirm_score();
    });

    $('#score-undo').click(function() {
        undo_score();
    });

    $('.rematch-offer').click(function() {
        socket.emit('send_rematch_offer', {hashid: hashid['hashid']});
        $('.rematch').hide();
        $('.rematch-sent').show();
    });

    socket.on('rematch_offer', function() {
        $('.rematch-offer').hide();
        $('.rematch-accept').show();
    });

    $('.rematch-accept').click(function() {
        $('.rematch-accept').hide();
        socket.emit('accept_rematch_offer', {hashid: hashid['hashid']});
    });

    socket.on('start_rematch', function(msg) {
        window.location.replace(game_url + msg['hashid']);
    });

    $('#appleActivateSound').click(function() {
        audio.play();
        $('#appleActivateSound').hide();
    });

    function getOS() {
        var userAgent = window.navigator.userAgent,
            platform = window.navigator.platform,
            macosPlatforms = ['Macintosh', 'MacIntel', 'MacPPC', 'Mac68K'],
            windowsPlatforms = ['Win32', 'Win64', 'Windows', 'WinCE'],
            iosPlatforms = ['iPhone', 'iPad', 'iPod'],
            os = null;
      
        if (macosPlatforms.indexOf(platform) !== -1) {
          os = 'Mac OS';
        } else if (iosPlatforms.indexOf(platform) !== -1) {
          os = 'iOS';
        } else if (windowsPlatforms.indexOf(platform) !== -1) {
          os = 'Windows';
        } else if (/Android/.test(userAgent)) {
          os = 'Android';
        } else if (!os && /Linux/.test(platform)) {
          os = 'Linux';
        }
      
        return os;
      }

    var os = getOS();
    if (os == 'Mac OS' || os == 'iOS') {
        $('#appleActivateSound').show();
    }


});







