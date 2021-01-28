$(document).ready(function() {
    // namespace for handling
    namespace = '/chat';

    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace, {transports: ['websocket']});

    var cdn_url = '';
    
    if (window.location.hostname == 'lidarts.org') {
        cdn_url = 'https://lidartsstatic.org'
    }

    var user_id = $('#user_id').data()['id'];
    var profile_url = $('#profile_url').data()['url'];
    var tournament_hashid = $('#tournament_hashid').data()['hashid'];
    var show_average_in_chat_list = $('#show_average_in_chat_list').data()['bool'];

    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    socket.on('connect', function () {
        socket.emit('init', {hashid: tournament_hashid});     
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
            
            if (show_average_in_chat_list == 'True') {
                player_average = '<small>Avg.: ' + msg['players'][user]['statistics']['average'] + '</small>';
            } else {
                player_average = '';
            }

            if (msg['players'][user]['country'] != null) {
                flag = '<img src="' + cdn_url + '/static/img/flags/' + msg['players'][user]['country'] + '.png" style="margin-right: 3px" class="' + country_flag_class + '">'
            } else {
                flag = ''
            };

            if (msg['players'][user]['is_backer']) {
                online_status_icon = '<i title="Lidarts backer" class="fas fa-star '
                backer_name_icon = '<i title="Lidarts backer" class="fas fa-star"></i>'
            } else {
                online_status_icon = '<i class="fas fa-circle '
                backer_name_icon = ''
            }

            $('#online_players').append('<div class="card"><div class="card-body" style="padding: 2px 2px 2px 2px;">'
                + '<button class="btn btn-warning"'
                + 'id="kickPlayer-' + msg['players'][user]['id'] + '" data-toggle="modal" data-target="#kickModal" '
                + 'data-userid="' + msg['players'][user]['id'] + '" '
                + 'data-username="' + msg['players'][user]['username'] + '">Kick</button>'
                + '<button class="btn btn-danger"'
                + 'id="banPlayer-' + msg['players'][user]['id'] + '" data-toggle="modal" data-target="#banModal" '
                + 'data-userid="' + msg['players'][user]['id'] + '" '
                + 'data-username="' + msg['players'][user]['username'] + '">Ban</button>'
                + '<strong style="font-size: 20px;"><a href="' + profile_url + msg['players'][user]['username'] + '" id="powertip-' + user + '" class="tooltips text-secondary" data-powertip="">'
                + '<img src="' + msg['players'][user]['avatar'] + '" height="50px" width="50px" class="avatar avatar-status avatar-status-' + msg['players'][user]['status'] + '">'
                + flag
                + backer_name_icon
                + msg['players'][user]['username'] + '</a></strong> '
                + player_average
                + '</div></div>');
        };  
    });

    $('#kickModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var username = button.data('username');
        var user_id = button.data('userid');
        var modal = $(this);
        modal.find('#kickPlayerName').text(username);
        modal.find('#kickPlayerButton').data('userid', user_id);
      });

      $('#banModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var username = button.data('username');
        var user_id = button.data('userid');
        var modal = $(this);
        modal.find('#banPlayerName').text(username);
        modal.find('#banPlayerButton').data('userid', user_id);
    });

    $('#unbanModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var username = button.data('username');
        var user_id = button.data('userid');
        var modal = $(this);
        modal.find('#unbanPlayerName').text(username);
        modal.find('#unbanPlayerButton').data('userid', user_id);
    });

    $('#kickPlayerButton').click( function () {
        var user_id = $(this).data('userid');
        socket.emit('kick_player', {hashid: tournament_hashid, user_id: user_id});
    });

    $('#banPlayerButton').click( function () {
        var user_id = $(this).data('userid');
        socket.emit('ban_player', {hashid: tournament_hashid, user_id: user_id});    
    });

    $('#unbanPlayerButton').click( function () {
        var user_id = $(this).data('userid');
        socket.emit('unban_player', {hashid: tournament_hashid, user_id: user_id});   
        $('#unban-' + user_id).hide(); 
    });

});
