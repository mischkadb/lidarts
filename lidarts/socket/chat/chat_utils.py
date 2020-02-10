# -*- coding: utf-8 -*-

"""Chat socket utilities."""

from datetime import datetime, timedelta

import bleach
from flask_socketio import emit

from lidarts import avatars, db
from lidarts.models import Notification, Privatemessage, User

# threshold in seconds on how long to count user as online
LAST_SEEN_ONLINE_THRESHOLD = 15


def broadcast_online_players():
    """Emit all online players to all online players."""
    online_players_dict = {}
    online_players = (
        User.query.
        filter(User.last_seen > (datetime.utcnow() - timedelta(seconds=LAST_SEEN_ONLINE_THRESHOLD))).
        all()
    )

    for user in online_players:
        status = user.status
        if user.last_seen_ingame and user.last_seen_ingame > (datetime.utcnow() - timedelta(seconds=10)):
            status = 'playing'
        avatar = avatars.url(user.avatar) if user.avatar else avatars.url('default.png')

        online_players_dict[user.id] = {
            'id': user.id,
            'username': user.username,
            'status': status,
            'avatar': avatar,
        }

    emit(
        'send_online_players',
        online_players_dict,
        broadcast=True,
        namespace='/chat',
    )


def send_notification(receiver_id, receiver_name, message, sender_id, type_):
    """Store and emit new notification to a user.

    Args:
        receiver_id: Receiver ID of notification
        receiver_name: Username of notification receiver
        message: Notification data for frontend; contains message text, author and type of notification
        sender_id: Notification author userID
        type_: Notification type, e.g. challenge, private message

    """
    notification = Notification(
        user=receiver_id,
        message=message,
        author=sender_id,
        type=type_,
    )

    db.session.add(notification)
    db.session.commit()

    emit(
        'send_notification',
        {'message': message, 'author': sender_id, 'type': type_},
        room=receiver_name,
        namespace='/base',
    )


def clean_message(message):
    """Message to be cleaned from harmful tags like <script> to prevent attacks like injections.

    Args:
        message: Message to be cleaned

    Returns:
        Cleaned message

    """
    # escape harmful tags like <script> to prevent attacks like injections
    # bleach standard settings still allow tags like <b> to style text, harder rules could be enforced
    return bleach.clean(message)


def store_private_message(message_text, sender_id, receiver_id):
    """Save private message to database.

    Args:
        message_text: Message to be saved
        sender_id: userID of sender
        receiver_id: userID of receiver

    """
    new_message = Privatemessage(
        message=message_text,
        sender=sender_id,
        receiver=receiver_id,
        timestamp=datetime.utcnow(),
    )

    db.session.add(new_message)
    db.session.commit()
