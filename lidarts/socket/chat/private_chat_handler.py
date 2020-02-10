# -*- coding: utf-8 -*-

"""Private Chat socket handler.

Saves and relays private messages.
"""

from datetime import datetime

from flask_login import current_user
from flask_socketio import emit, join_room

from lidarts import socketio
from lidarts.models import User
from lidarts.socket.chat.chat_utils import clean_message, send_notification, store_private_message


@socketio.on('connect', namespace='/private_messages')
def connect_private_messages_room():
    """Conncect user to his own room for PM communication."""
    if current_user.is_authenticated:
        join_room(current_user.username)


# move this to utils?
class ChatUser(object):
    """Chat user with userID and username."""

    def __init__(self, id_, name):
        """Set id and name of Chat user.

        Args:
            id_: userID
            name: username
        """
        self.id_ = id_
        self.name = name


@socketio.on('broadcast_private_message', namespace='/private_messages')
def send_private_message(message):
    """Save and relay chat message in private chat.

    Args:
        message: Message sent by one player.
                 Contains message, author userID, receiver userID and game hashID.
    """
    # escape harmful tags like <script> to prevent attacks like injections
    # bleach standard settings still allow tags like <b> to style text, harder rules could be enforced
    message_text = clean_message(message['message'])

    receiver_name = (
        User.query.
        with_entities(User.username).
        filter_by(id=message['receiver']).
        first_or_404()[0]
    )

    sender = ChatUser(current_user.id, current_user.username)
    receiver = ChatUser(message['receiver'], receiver_name)

    store_private_message(message_text, sender.id_, receiver.id_)

    send_notification(receiver.id_, receiver_name, message_text, sender.id_, 'message')

    emit_data = {
        'message': message_text,
        'sender': sender.id_,
        'sender_name': sender.name,
        'receiver_name': receiver.name,
        'receiver': receiver.id_,
        'timestamp': f'{str(datetime.utcnow())}Z',
    }

    emit(
        'broadcast_private_message',
        emit_data,
        room=receiver.name,
        broadcast=True,
    )

    emit(
        'broadcast_private_message',
        emit_data,
        room=sender.name,
        broadcast=True,
    )
