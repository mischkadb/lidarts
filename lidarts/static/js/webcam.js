$(document).ready(function() {
    var hashid = $('#jitsi-hashid').data()['hashid'];
    var flip = $('#local-video-flip').data()['flip'];
    if (flip == 'True') {
        flip = true;
    } else {
        flip = false;
    }

    configoverwrite = {
        disableLocalVideoFlip: flip,
    }

    ifaceoverwrite = {
        TOOLBAR_BUTTONS: [ 'microphone', 'camera', 
        'fodeviceselection', 
        'settings',
        'tileview',
        'videoquality'],
        GENERATE_ROOMNAMES_ON_WELCOME_PAGE: false,
        DISPLAY_WELCOME_PAGE_CONTENT: false,
        INVITATION_POWERED_BY: false,
        AUTHENTICATION_ENABLE: false,
        DISABLE_RINGING: true,
        DISPLAY_WELCOME_PAGE_CONTENT: false,
        DISPLAY_WELCOME_PAGE_TOOLBAR_ADDITIONAL_CONTENT: false,
    }

    const domain = 'meet.jit.si';
    const options = {
        roomName: 'lidarts-' + hashid,
        parentNode: document.querySelector('#meet'),
        noSSL: false,
        configOverwrite: configoverwrite,
        interfaceConfigOverwrite: ifaceoverwrite,
    };
    const api = new JitsiMeetExternalAPI(domain, options);
});







