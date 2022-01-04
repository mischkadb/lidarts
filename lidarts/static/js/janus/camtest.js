var server = null;
server = "wss://janus1.lidarts.org/socket";

var janus = null;
var echotest = null;
var opaqueId = "devicetest-"+Janus.randomString(12);

var bitrateTimer = null;
var spinner = null;

var audioDeviceId = null;
var videoDeviceId = null;

var audioenabled = false;
var videoenabled = false;

var acodec = (getQueryStringValue("acodec") !== "" ? getQueryStringValue("acodec") : null);
var vcodec = (getQueryStringValue("vcodec") !== "" ? getQueryStringValue("vcodec") : null);
var vprofile = (getQueryStringValue("vprofile") !== "" ? getQueryStringValue("vprofile") : null);

// Helper method to prepare a UI selection of the available devices
function initDevices(devices) {
	$('#devices').removeClass('hide');
	$('#devices').parent().removeClass('hide');
	$('#choose-device').click(restartCapture);
	var audio = $('#audio-device').val();
	var video = $('#video-device').val();
	$('#audio-device, #video-device').find('option').remove();

	devices.forEach(function(device) {
		var label = device.label;
		if(!label || label === "")
			label = device.deviceId;
		var option = $('<option value="' + device.deviceId + '">' + label + '</option>');
		if(device.kind === 'audioinput') {
			$('#audio-device').append(option);
		} else if(device.kind === 'videoinput') {
			$('#video-device').append(option);
		} else if(device.kind === 'audiooutput') {
			// Apparently only available from Chrome 49 on?
			// https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/setSinkId
			// Definitely missing in Safari at the moment: https://bugs.webkit.org/show_bug.cgi?id=179415
			$('#output-devices').removeClass('hide');
			$('#audiooutput').append('<li><a href="#" id="' + device.deviceId + '">' + label + '</a></li>');
			$('#audiooutput a').unbind('click')
				.click(function() {
					var deviceId = $(this).attr("id");
					var label = $(this).text();
					Janus.log("Trying to set device " + deviceId + " (" + label + ") as sink for the output");
					if($('#peervideo').length === 0) {
						Janus.error("No remote video element available");
						bootbox.alert("No remote video element available");
						return false;
					}
					if(!$('#peervideo').get(0).setSinkId) {
						Janus.error("SetSinkId not supported");
						bootbox.warn("SetSinkId not supported");
						return false;
					}
					$('#peervideo').get(0).setSinkId(deviceId)
						.then(function() {
							Janus.log('Audio output device attached:', deviceId);
							$('#outputdeviceset').html(label + '<span class="caret"></span>').parent().removeClass('open');
						}).catch(function(error) {
							Janus.error(error);
							bootbox.alert(error);
						});
					return false;
				});
		}
	});

	$('#audio-device').val(audio);
	$('#video-device').val(video);

	$('#change-devices').click(function() {
		// A different device has been selected: hangup the session, and set it up again
		$('#audio-device, #video-device').attr('disabled', true);
		$('#change-devices').attr('disabled', true);
		restartCapture();
	});
}

function restartCapture() {
	// Negotiate WebRTC
	var body = { audio: true, video: true };
	// We can try and force a specific codec, by telling the plugin what we'd prefer
	// For simplicity, you can set it via a query string (e.g., ?vcodec=vp9)
	if(acodec)
		body["audiocodec"] = acodec;
	if(vcodec)
		body["videocodec"] = vcodec;
	// For the codecs that support them (VP9 and H.264) you can specify a codec
	// profile as well (e.g., ?vprofile=2 for VP9, or ?vprofile=42e01f for H.264)
	if(vprofile)
		body["videoprofile"] = vprofile;
	Janus.debug("Sending message:", body);
	echotest.send({ message: body });
	Janus.debug("Trying a createOffer too (audio/video sendrecv)");
	var replaceAudio = $('#audio-device').val() !== audioDeviceId;
	audioDeviceId = $('#audio-device').val();
	var replaceVideo = $('#video-device').val() !== videoDeviceId;
	videoDeviceId = $('#video-device').val();
	echotest.createOffer(
		{
			// We provide a specific device ID for both audio and video
			media: {
				audio: {
					deviceId: {
						exact: audioDeviceId
					}
				},
				replaceAudio: replaceAudio,	// This is only needed in case of a renegotiation
				video: {
					deviceId: {
						exact: videoDeviceId
					}
				},
				replaceVideo: replaceVideo,	// This is only needed in case of a renegotiation
				data: true	// Let's negotiate data channels as well
			},
			success: function(jsep) {
				Janus.debug("Got SDP!", jsep);
				echotest.send({ message: body, jsep: jsep });
			},
			error: function(error) {
				Janus.error("WebRTC error:", error);
				bootbox.alert("WebRTC error... " + error.message);
			}
		});
}

$(document).ready(function() {
	// Initialize the library (all console debuggers enabled)
	Janus.init({debug: "all", callback: function() {
		// Use a button to start the demo
		$('#start').one('click', function() {
			$(this).attr('disabled', true).unbind('click');
			// Make sure the browser supports WebRTC
			if(!Janus.isWebrtcSupported()) {
				bootbox.alert("No WebRTC support... ");
				return;
			}
			// Create session
			janus = new Janus(
				{
					server: server,
					// No "iceServers" is provided, meaning janus.js will use a default STUN server
					// Here are some examples of how an iceServers field may look like to support TURN
					// 		iceServers: [{urls: "turn:yourturnserver.com:3478", username: "janususer", credential: "januspwd"}],
					// 		iceServers: [{urls: "turn:yourturnserver.com:443?transport=tcp", username: "janususer", credential: "januspwd"}],
					// 		iceServers: [{urls: "turns:yourturnserver.com:443?transport=tcp", username: "janususer", credential: "januspwd"}],
					// Should the Janus API require authentication, you can specify either the API secret or user token here too
					//		token: "mytoken",
					//	or
					//		apisecret: "serversecret",
					success: function() {
						// Attach to EchoTest plugin
						janus.attach(
							{
								plugin: "janus.plugin.echotest",
								opaqueId: opaqueId,
								success: function(pluginHandle) {
									$('#details').remove();
									echotest = pluginHandle;
									Janus.log("Plugin attached! (" + echotest.getPlugin() + ", id=" + echotest.getId() + ")");
									// Enumerate devices: that's what we're here for
									Janus.listDevices(initDevices);
									// We wait for the user to select the first device before making a move
									$('#start').removeAttr('disabled').html("Stop")
										.click(function() {
											$(this).attr('disabled', true);
											if(bitrateTimer)
												clearInterval(bitrateTimer);
											bitrateTimer = null;
											janus.destroy();
										});
								},
								error: function(error) {
									console.error("  -- Error attaching plugin...", error);
									bootbox.alert("Error attaching plugin... " + error);
								},
								consentDialog: function(on) {
									Janus.debug("Consent dialog should be " + (on ? "on" : "off") + " now");
									if(on) {
										// Darken screen and show hint
										$.blockUI({
											message: '<div><img src="up_arrow.png"/></div>',
											css: {
												border: 'none',
												padding: '15px',
												backgroundColor: 'transparent',
												color: '#aaa',
												top: '10px',
												left: (navigator.mozGetUserMedia ? '-100px' : '300px')
											} });
									} else {
										// Restore screen
										$.unblockUI();
									}
								},
								iceState: function(state) {
									Janus.log("ICE state changed to " + state);
								},
								mediaState: function(medium, on) {
									Janus.log("Janus " + (on ? "started" : "stopped") + " receiving our " + medium);
								},
								webrtcState: function(on) {
									Janus.log("Janus says our WebRTC PeerConnection is " + (on ? "up" : "down") + " now");
									$("#videoleft").parent().unblock();
								},
								slowLink: function(uplink, lost) {
									Janus.warn("Janus reports problems " + (uplink ? "sending" : "receiving") +
										" packets on this PeerConnection (" + lost + " lost packets)");
								},
								onmessage: function(msg, jsep) {
									Janus.debug(" ::: Got a message :::", msg);
									if(jsep) {
										Janus.debug("Handling SDP as well...", jsep);
										echotest.handleRemoteJsep({ jsep: jsep });
									}
									var result = msg["result"];
									if(result) {
										if(result === "done") {
											// The plugin closed the echo test
											bootbox.alert("The Echo Test is over");
											if(spinner)
												spinner.stop();
											spinner = null;
											$('#myvideo').remove();
											$('#waitingvideo').remove();
											$('#peervideo').remove();
											audioenabled = true;
											$('#toggleaudio').attr('disabled', true).html("Disable audio").removeClass("btn-success").addClass("btn-danger");
											videoenabled = true;
											$('#togglevideo').attr('disabled', true).html("Disable video").removeClass("btn-success").addClass("btn-danger");
											$('#bitrate').attr('disabled', true);
											$('#bitrateset').html('Bandwidth<span class="caret"></span>');
											$('#curbitrate').hide();
											if(bitrateTimer)
												clearInterval(bitrateTimer);
											bitrateTimer = null;
											$('#curres').hide();
											$('#datasend').val('').attr('disabled', true);
											$('#datarecv').val('');
											$('#outputdeviceset').html('Output device<span class="caret"></span>');
											return;
										}
										// Any loss?
										var status = result["status"];
										if(status === "slow_link") {
											toastr.warning("Janus apparently missed many packets we sent, maybe we should reduce the bitrate", "Packet loss?", {timeOut: 2000});
										}
									}
								},
								onlocalstream: function(stream) {
									Janus.debug(" ::: Got a local stream :::", stream);
									if($('#myvideo').length === 0) {
										$('#videos').removeClass('hide').show();
										$('#videoleft').append('<video class="rounded centered" id="myvideo" width="100%" height="100%" autoplay playsinline muted="muted"/>');
									}
									Janus.attachMediaStream($('#myvideo').get(0), stream);
									$("#myvideo").get(0).muted = "muted";
									if(echotest.webrtcStuff.pc.iceConnectionState !== "completed" &&
											echotest.webrtcStuff.pc.iceConnectionState !== "connected") {
										// No remote video yet
										$('#videoright').append('<video class="rounded centered" id="waitingvideo" width="100%" height="100%" />');
										if(spinner == null) {
											var target = document.getElementById('videoright');
											spinner = new Spinner({top:100}).spin(target);
										} else {
											spinner.spin();
										}
										var videoTracks = stream.getVideoTracks();
										if(!videoTracks || videoTracks.length === 0) {
											// No webcam
											$('#myvideo').hide();
											$('#videoleft').append(
												'<div class="no-video-container">' +
													'<i class="fa fa-video-camera fa-5 no-video-icon"></i>' +
													'<span class="no-video-text">No webcam available</span>' +
												'</div>');
										}
									}
									var videoTracks = stream.getVideoTracks();
									if(!videoTracks || videoTracks.length === 0) {
										// No webcam
										$('#myvideo').hide();
										if($('#videoleft .no-video-container').length === 0) {
											$('#videoleft').append(
												'<div class="no-video-container">' +
													'<i class="fa fa-video-camera fa-5 no-video-icon"></i>' +
													'<span class="no-video-text">No webcam available</span>' +
												'</div>');
										}
									} else {
										$('#videoleft .no-video-container').remove();
										$('#myvideo').removeClass('hide').show();
									}
									// Reset devices controls
									$('#audio-device, #video-device').removeAttr('disabled');
									$('#change-devices').removeAttr('disabled');
								},
								onremotestream: function(stream) {
									Janus.debug(" ::: Got a remote stream :::", stream);
									var addButtons = false;
									if($('#peervideo').length === 0) {
										addButtons = true;
										$('#videos').removeClass('hide').show();
										$('#videoright').append('<video class="rounded centered hide" id="peervideo" width="100%" height="100%" autoplay playsinline/>');
										// Show the video, hide the spinner and show the resolution when we get a playing event
										$("#peervideo").bind("playing", function () {
											$('#waitingvideo').remove();
											if(this.videoWidth)
												$('#peervideo').removeClass('hide').show();
											if(spinner)
												spinner.stop();
											spinner = null;
											var width = this.videoWidth;
											var height = this.videoHeight;
											$('#curres').removeClass('hide').text(width+'x'+height).show();
										});
									}
									Janus.attachMediaStream($('#peervideo').get(0), stream);
									var videoTracks = stream.getVideoTracks();
									if(!videoTracks || videoTracks.length === 0) {
										// No remote video
										$('#peervideo').hide();
										if($('#videoright .no-video-container').length === 0) {
											$('#videoright').append(
												'<div class="no-video-container">' +
													'<i class="fa fa-video-camera fa-5 no-video-icon"></i>' +
													'<span class="no-video-text">No remote video available</span>' +
												'</div>');
										}
									} else {
										$('#videoright .no-video-container').remove();
										$('#peervideo').removeClass('hide').show();
									}
									if(!addButtons)
										return;
									// Enable audio/video buttons and bitrate limiter
									audioenabled = true;
									videoenabled = true;
									$('#toggleaudio').removeAttr('disabled').click(
										function() {
											audioenabled = !audioenabled;
											if(audioenabled)
												$('#toggleaudio').html("Disable audio").removeClass("btn-success").addClass("btn-danger");
											else
												$('#toggleaudio').html("Enable audio").removeClass("btn-danger").addClass("btn-success");
											echotest.send({ message: { audio: audioenabled }});
										});
									$('#togglevideo').removeAttr('disabled').click(
										function() {
											videoenabled = !videoenabled;
											if(videoenabled)
												$('#togglevideo').html("Disable video").removeClass("btn-success").addClass("btn-danger");
											else
												$('#togglevideo').html("Enable video").removeClass("btn-danger").addClass("btn-success");
											echotest.send({ message: { video: videoenabled }});
										});
									$('#toggleaudio').parent().removeClass('hide').show();
									$('#bitrate a').removeAttr('disabled').click(function() {
										var id = $(this).attr("id");
										var bitrate = parseInt(id)*1000;
										if(bitrate === 0) {
											Janus.log("Not limiting bandwidth via REMB");
										} else {
											Janus.log("Capping bandwidth to " + bitrate + " via REMB");
										}
										$('#bitrateset').html($(this).html() + '<span class="caret"></span>').parent().removeClass('open');
										echotest.send({ message: { bitrate: bitrate }});
										return false;
									});
									if(Janus.webRTCAdapter.browserDetails.browser === "chrome" || Janus.webRTCAdapter.browserDetails.browser === "firefox" ||
											Janus.webRTCAdapter.browserDetails.browser === "safari") {
										$('#curbitrate').removeClass('hide').show();
										bitrateTimer = setInterval(function() {
											// Display updated bitrate, if supported
											var bitrate = echotest.getBitrate();
											$('#curbitrate').text(bitrate);
											// Check if the resolution changed too
											var width = $("#peervideo").get(0).videoWidth;
											var height = $("#peervideo").get(0).videoHeight;
											if(width > 0 && height > 0)
												$('#curres').removeClass('hide').text(width+'x'+height).show();
										}, 1000);
									}
								},
								ondataopen: function(data) {
									Janus.log("The DataChannel is available!");
									$('#videos').removeClass('hide').show();
									$('#datasend').removeAttr('disabled');
								},
								ondata: function(data) {
									Janus.debug("We got data from the DataChannel!", data);
									$('#datarecv').val(data);
								},
								oncleanup: function() {
									Janus.log(" ::: Got a cleanup notification :::");
									if(spinner)
										spinner.stop();
									spinner = null;
									$('#myvideo').remove();
									$('#waitingvideo').remove();
									$('#peervideo').remove();
									$('.no-video-container').remove();
									audioenabled = true;
									$('#toggleaudio').attr('disabled', true).html("Disable audio").removeClass("btn-success").addClass("btn-danger");
									videoenabled = true;
									$('#togglevideo').attr('disabled', true).html("Disable video").removeClass("btn-success").addClass("btn-danger");
									$('#bitrate').attr('disabled', true);
									$('#bitrateset').html('Bandwidth<span class="caret"></span>');
									$('#curbitrate').hide();
									if(bitrateTimer)
										clearInterval(bitrateTimer);
									bitrateTimer = null;
									$('#curres').hide();
									$('#datasend').val('').attr('disabled', true);
									$('#datarecv').val('');
									$('#outputdeviceset').html('Output device<span class="caret"></span>');
								}
							});
					},
					error: function(error) {
						Janus.error(error);
						bootbox.alert(error, function() {
							window.location.reload();
						});
					},
					destroyed: function() {
						window.location.reload();
					}
				});
		});
	}});
});

function checkEnter(event) {
	var theCode = event.keyCode ? event.keyCode : event.which ? event.which : event.charCode;
	if(theCode == 13) {
		sendData();
		return false;
	} else {
		return true;
	}
}

function sendData() {
	var data = $('#datasend').val();
	if(data === "") {
		bootbox.alert('Insert a message to send on the DataChannel');
		return;
	}
	echotest.data({
		text: data,
		error: function(reason) { bootbox.alert(reason); },
		success: function() { $('#datasend').val(''); },
	});
}

// Helper to parse query string
function getQueryStringValue(name) {
	name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
	var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
		results = regex.exec(location.search);
	return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}
