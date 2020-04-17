$(document).ready(function() {
    var hashid = $('#jitsi-settings').data()['hashid'];
    
    var jitsi_app = $('#jitsi-settings').data()['app'];
    if (jitsi_app == 'True') {
        jitsi_app = true;
    } else {
        jitsi_app = false;
    }

    configoverwrite = {
        // disableDeepLinking enables Jitsi on mobile browsers
        // needs to be false for app notice
        disableDeepLinking: !jitsi_app,
    }

    ifaceoverwrite = {
        TOOLBAR_BUTTONS: [ 'microphone', 'camera', 
        'fodeviceselection', 'fullscreen',
        'settings', 'livestreaming',
        'tileview',
        'videoquality'],
        GENERATE_ROOMNAMES_ON_WELCOME_PAGE: false,
        DISPLAY_WELCOME_PAGE_CONTENT: false,
        INVITATION_POWERED_BY: false,
        AUTHENTICATION_ENABLE: false,
        DISABLE_RINGING: true,
        DISPLAY_WELCOME_PAGE_CONTENT: false,
        DISPLAY_WELCOME_PAGE_TOOLBAR_ADDITIONAL_CONTENT: false,
        MOBILE_APP_PROMO: jitsi_app,
        MAXIMUM_ZOOMING_COEFFICIENT: 1.0,
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







