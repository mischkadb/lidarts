$(document).ready(function() {


    // Handler for the score input form.
    var remove_friend_url = $('#remove_friend_url').data()['url'];
    var remove_friend_request_url = $('#remove_friend_request_url').data()['url'];

    $('.button-remove-friend').click( function (event) {
        var id = this.id.replace('button-remove-friend-', '');

        $.post(remove_friend_url + id,
            function() {
                $(document.getElementById('element-remove-friend-' + id)).html('<strong style="color: #449944">Friend removed.</strong>');
            }
        );
    });

    $('.button-remove-friend-request').click( function (event) {
        var id = this.id.replace('button-remove-friend-request-', '');

        $.post(remove_friend_request_url + id,
            function() {
                $(document.getElementById('element-remove-friend-request-' + id)).html('<strong style="color: #bb4444">Request removed.</strong>');
            }
        );
    });
});