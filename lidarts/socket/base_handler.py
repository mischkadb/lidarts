# from flask import request
from lidarts import socketio, db
from flask_login import current_user
from flask_socketio import emit, join_room
from lidarts.socket.utils import send_notification
from lidarts.models import Notification
from datetime import datetime


@socketio.on('connect', namespace='/base')
def connect():
    # print('Client connected', request.sid)
    if current_user.is_authenticated:
        join_room(current_user.username)
        current_user.active_sessions += 1
        notifications = Notification.query.filter_by(user=current_user.id).all()
        for notification in notifications:
            send_notification(current_user.username, notification.message, notification.author, notification.type)
        db.session.commit()
        # broadcast_online_players()


@socketio.on('user_heartbeat', namespace='/base')
def connect():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        # this causes issues in chat
        # broadcast_online_players()


@socketio.on('get_status', namespace='/base')
def get_status():
    if current_user.is_authenticated:
        emit('status_reply', {'status': current_user.status})


@socketio.on('disconnect', namespace='/base')
def disconnect():
    # print('Client disconnected', request.sid)
    if current_user.is_authenticated:
        current_user.active_sessions -= 1
        db.session.commit()
        # broadcast_online_players()
