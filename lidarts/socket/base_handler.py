# from flask import request
from lidarts import socketio, db
from flask_login import current_user
from flask_socketio import disconnect, emit, join_room, ConnectionRefusedError
from lidarts.socket.utils import send_notification
from lidarts.models import Notification, SocketConnections, UserSettings
from datetime import datetime


@socketio.on('connect', namespace='/base')
def connect_client():
    if current_user.is_authenticated:
        current_user.ping()

        join_room(current_user.username)
        notifications = Notification.query.filter_by(user=current_user.id).all()
        for notification in notifications:
            send_notification(current_user.username, notification.message, notification.author, notification.type, silent=True)

        emit('status_reply', {'status': current_user.status})


@socketio.on('init', namespace='/base')
def init():
    if current_user.is_authenticated:
        settings = (
            UserSettings.query
            .filter_by(user=current_user.id).first()
        )
        if not settings:
            settings = UserSettings(user=current_user.id)
            db.session.add(settings)
            db.session.commit()
        notication_sound = settings.notification_sound
        emit(
            'settings',
            {'notification_sound': notication_sound, }
        )


@socketio.on('user_heartbeat', namespace='/base')
def heartbeat():
    if current_user.is_authenticated:
        current_user.ping()


@socketio.on('disconnect', namespace='/base')
def disconnect_client():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        current_user.is_online = False
        db.session.commit()
