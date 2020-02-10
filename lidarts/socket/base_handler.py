# -*- coding: utf-8 -*-

"""Base socket used on entire site.

Needed for notifications, status updates etc.
"""

from datetime import datetime

from flask_login import current_user
from flask_socketio import emit, join_room

from lidarts import db, socketio
from lidarts.models import Notification
from lidarts.socket.chat.chat_utils import send_notification


@socketio.on('connect', namespace='/base')
def connect():
    """Socket conenction handler.

    Sends new notifications.
    """
    if current_user.is_authenticated:
        join_room(current_user.username)
        notifications = Notification.query.filter_by(user=current_user.id).all()
        for notification in notifications:
            send_notification(current_user.username, notification.message, notification.author, notification.type)
        db.session.commit()


@socketio.on('user_heartbeat', namespace='/base')
def heartbeat():
    """User heartbeat handler.

    User sends heartbeat every few seconds.
    Used to track when user was last seen for status indication.
    """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@socketio.on('get_status', namespace='/base')
def get_status():
    """User status to frontend request handler."""
    if current_user.is_authenticated:
        emit('status_reply', {'status': current_user.status})
