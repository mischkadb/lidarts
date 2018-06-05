$(document).ready(function() {


    // Handler for the score input form.
    var accept_url = $('#accept_url').data()['url'];
    var decline_url = $('#decline_url').data()['url'];
    var decline_challenge_url = $('#decline_challenge_url').data()['url'];

    $('.button-accept-friend-request').click( function (event) {
        var id = event.target.id.replace('button-accept-friend-request-', '');

        $.post(accept_url + id,
            function() {
                $(document.getElementById('element-friend-request-' + id)).html('<strong style="color: #449944">Request accepted.</strong>');
            }
        );
    });

    $('.button-decline-friend-request').click( function (event) {
        var id = event.target.id.replace('button-decline-friend-request-', '');

        $.post(decline_url + id,
            function() {
                $(document.getElementById('element-friend-request-' + id)).html('<strong style="color: #bb4444">Request declined.</strong>');
            }
        );
    });

    $('.decline-challenge').click( function (event) {
        var id = event.target.id.replace('decline-challenge-', '');
        console.log(id);

        $.post(decline_challenge_url + id,
            function() {
                $(document.getElementById('element-decline-challenge-' + id)).html('<strong style="color: #bb4444">Challenge declined.</strong>');
            }
        );
    });


});