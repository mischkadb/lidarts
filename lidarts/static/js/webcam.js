$(document).ready(function() {
    var hashid = $('#jitsi-hashid').data()['hashid'];

    ifaceoverwrite = {
        TOOLBAR_BUTTONS: [ 'microphone', 'camera', 
        'fodeviceselection', 
        'settings',
        'videoquality'],
        GENERATE_ROOMNAMES_ON_WELCOME_PAGE: false,
        DISPLAY_WELCOME_PAGE_CONTENT: false,
        INVITATION_POWERED_BY: false,
        AUTHENTICATION_ENABLE: false,
        DISABLE_RINGING: true,
    }

    const domain = 'meet.jit.si';
    const options = {
        roomName: 'lidarts-' + hashid,
        parentNode: document.querySelector('#meet'),
        noSSL: false,
        height: 800,
        interfaceConfigOverwrite: ifaceoverwrite,
    };
    const api = new JitsiMeetExternalAPI(domain, options);
});







