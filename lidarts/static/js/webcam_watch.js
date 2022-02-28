$(document).ready(function() {
    var hashid = $('#jitsi-settings').data()['hashid'];
    var public_server = $('#jitsi-settings').data()['public_server'];
    var force_public_server = $('#jitsi-settings').data()['force_public_server'];
    if (public_server == 'True' || force_public_server == 'True') {        
        domain = 'meet.jit.si';
        public_server = true;
    } else {
        domain = 'jitsi.dusk-server.de'
        public_server = false;
    }
    
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
        startWithAudioMuted: true,
        startWithVideoMuted: true,
        disableInitialGUM: true,
    }

    ifaceoverwrite = {
        TOOLBAR_BUTTONS: [ 'fullscreen',
        'settings',
        'tileview',
        'videoquality'],
        GENERATE_ROOMNAMES_ON_WELCOME_PAGE: false,
        INVITATION_POWERED_BY: false,
        AUTHENTICATION_ENABLE: false,
        DISABLE_RINGING: true,
        DISPLAY_WELCOME_PAGE_CONTENT: false,
        DISPLAY_WELCOME_PAGE_TOOLBAR_ADDITIONAL_CONTENT: false,
        MOBILE_APP_PROMO: jitsi_app,
        MAXIMUM_ZOOMING_COEFFICIENT: 1.0,
        SHOW_CHROME_EXTENSION_BANNER: false,
        SHOW_JITSI_WATERMARK: public_server,
        SHOW_WATERMARK_FOR_GUESTS: public_server,
    }

    const options = {
        roomName: 'lidarts-' + hashid,
        parentNode: document.querySelector('#meet'),
        noSSL: false,
        configOverwrite: configoverwrite,
        interfaceConfigOverwrite: ifaceoverwrite,
    };
    const api = new JitsiMeetExternalAPI(domain, options);
    api.executeCommand('subject', ' ');
});







