$(document).ready(function () {
    var hashid = $('#jitsi-settings').data()['hashid'];
    var public_server = $('#jitsi-settings').data()['public_server'];
    var force_public_server = $('#jitsi-settings').data()['force_public_server'];
    domain = 'jitsi1.lidarts.org'

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
        TOOLBAR_BUTTONS: ['microphone', 'camera',
            'fodeviceselection', 'fullscreen',
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
        SHOW_JITSI_WATERMARK: false,
        SHOW_WATERMARK_FOR_GUESTS: false,
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







