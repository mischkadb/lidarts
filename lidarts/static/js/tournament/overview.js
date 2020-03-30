$(document).ready(function() {

    $('#public_tournament').click(function() {
        if ($('#public_tournament.custom-control-input')[0].checked) {
            $('.visible-public-only').removeClass('d-none');
        } else {
            $('.visible-public-only').addClass('d-none');
        }
    });
});
