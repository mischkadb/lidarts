$(document).ready(function() {

    $('#send_friend_request').click( function (event) {
        var user_id = $('#profile_user_id').data()['id'];
        var send_request_url = $('#send_request_url').data()['url'];

        $.post(send_request_url + user_id)
            .done(function() {
                $(document.getElementById('send_friend_request')).html('<strong style="color: #449944">Request sent.</strong>');
            });
    });

    $('.button-accept-friend-request').click( function (event) {
        var accept_url = $('#accept_url').data()['url'];
        var id = this.id.replace('button-accept-friend-request-', '');

        $.post(accept_url + id,
            function() {
                $(document.getElementById('element-friend-request-' + id)).html('<strong style="color: #449944">Request accepted.</strong>');
            }
        );
    });

    $('.button-decline-friend-request').click( function (event) {
        var decline_url = $('#decline_url').data()['url'];
        var id = this.id.replace('button-decline-friend-request-', '');

        $.post(decline_url + id,
            function() {
                $(document.getElementById('element-friend-request-' + id)).html('<strong style="color: #bb4444">Request declined.</strong>');
            }
        );
    });

    $('.decline-challenge').click( function (event) {
        var decline_challenge_url = $('#decline_challenge_url').data()['url'];
        var hashid = this.id.replace('decline-challenge-', '');

        $.post(decline_challenge_url + hashid,
            function() {
                $(document.getElementById('element-decline-challenge-' + hashid)).html('<strong style="color: #bb4444">Challenge declined.</strong>');
            }
        );
    });


});