from lidarts import socketio, db
from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room
from lidarts.models import WebcamSettings


@socketio.on('connect', namespace='/webcam_follow')
def connect():
    join_room(current_user.id)


@socketio.on('request_camera', namespace='/webcam_follow')
def request_camera(message):
    user_id = message['user_id']
    hashid = message['hashid']
    settings = (
        WebcamSettings.query
        .filter_by(user=user_id).first()
    )
    settings.latest_jitsi_hashid = hashid
    db.session.commit()
    emit('force_reload', room=user_id)
