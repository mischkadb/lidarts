# from flask import request
from lidarts import socketio, db
from flask_login import current_user
from flask_socketio import disconnect, emit, join_room, ConnectionRefusedError
from lidarts.socket.utils import send_notification
from lidarts.models import Notification, SocketConnections
from datetime import datetime


@socketio.on('connect', namespace='/base')
def connect_client():
    connections = SocketConnections.query.first()
    connections.active += 1
    connections.total += 1

    if not current_user.is_authenticated:
        db.session.commit()
        return

    current_user.ping()

    emit('status_reply', {'status': current_user.status})

    join_room(current_user.username)
    notifications = Notification.query.filter_by(user=current_user.id).all()
    for notification in notifications:
        send_notification(current_user.username, notification.message, notification.author, notification.type)


@socketio.on('disconnect', namespace='/base')
def disconnect_client():
    connections = SocketConnections.query.first()
    connections.active -= 1    

    if not current_user.is_authenticated:
        db.session.commit()
        return

    current_user.last_seen = datetime.utcnow()
    current_user.is_online = False
    db.session.commit()
