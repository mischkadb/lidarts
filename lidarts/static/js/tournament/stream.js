$(document).ready(function() {
    var api_key_url = $('#api_key_url').data()['url'];

    $('#generateAPIKeyButton').click( function () {
        $.ajax({
            url: api_key_url,
            type: "GET",
            success: function(api_key){
                $('#api_key').val(api_key);
            }
        })
    });
});

function copyLink() {
    var copyText = document.getElementById("api_key");
 
   /* Select the text field */
   copyText.select();
 
   /* Copy the text inside the text field */
   document.execCommand("copy");
 }
