// Hide two clear legs options in X fixed legs mode
if ($('#x_legs-tab').hasClass('active')) {
    $('#twoClearLegsForm').hide();
    $('#wcModeForm').hide();
}

$('#goal-tab button').on('shown.bs.tab', function (event) {
    var targetId = $(event.target).attr('id');

    var value = targetId.replace('-tab', '');

    // Setze den Wert des SelectFields
    $('#goal_mode').val(value);

    if (targetId === 'x_legs-tab') {
        $('#twoClearLegsForm').hide();
        $('#wcModeForm').hide();
    } else {
        $('#twoClearLegsForm').show();
        $('#wcModeForm').show();
    }
});
