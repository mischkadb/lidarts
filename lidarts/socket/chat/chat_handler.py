# -*- coding: utf-8 -*-

"""Public chat socket handler.

Saves and relays chat messages in public chat to all online users.
"""

from datetime import datetime

from flask_socketio import emit

from lidarts import db, socketio
from lidarts.models import Chatmessage, User
from lidarts.socket.chat.chat_utils import broadcast_online_players, clean_message


@socketio.on('connect', namespace='/chat')
def connect():
    """Broadcast new online status to all clients."""
    broadcast_online_players()


@socketio.on('broadcast_chat_message', namespace='/chat')
def broadcast_chat_message(message):
    """Broadcast new public chat message to all clients.

    Args:
        message: Public message sent by the user.
    """
    # escape harmful tags like <script> to prevent attacks like injections
    # bleach standard settings still allow tags like <b> to style text, harder rules could be enforced
    message_text = clean_message(message['message'])
    new_message = Chatmessage(message=message_text, author=message['user_id'], timestamp=datetime.utcnow())
    db.session.add(new_message)
    db.session.commit()

    # flake8 complains about lines starting with a dot, but it's arguably more readable
    # ignore that warning?
    author = (
        User.query.
        with_entities(User.username).
        filter_by(id=new_message.author).
        first_or_404()[0]
    )

    emit_data = {
        'author': author,
        'message': new_message.message,
        'timestamp': f'{str(new_message.timestamp)}Z',
    }

    emit('send_message', emit_data, broadcast=True)
