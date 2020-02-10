# -*- coding: utf-8 -*-

"""Chat socket handler.

Needed for notifications, status updates etc.
"""

from datetime import datetime

import bleach
from flask_login import current_user
from flask_socketio import emit, join_room

from lidarts import db, socketio
from lidarts.models import Chatmessage, ChatmessageIngame, Game, Notification, Privatemessage, User
from lidarts.socket.utils import broadcast_online_players, send_notification


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
    message_text = bleach.clean(message['message'])
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


@socketio.on('connect', namespace='/private_messages')
def connect_private_messages_room():
    """Conncect user to his own room for PM communication."""
    if current_user.is_authenticated:
        join_room(current_user.username)


@socketio.on('init', namespace='/game_chat')
def init(message):
    """Conncect user to active game room for game chat communication.

    Args:
        message: Contains current game hashid.
    """
    game = Game.query.filter_by(hashid=message['hashid']).first_or_404()
    join_room(game.hashid)


@socketio.on('broadcast_game_chat_message', namespace='/game_chat')
def send_game_chat_message(message):
    """Save and relay chat message in game chat.

    Args:
        message: Message sent by one player. Contains message, author userID and game hashID.
    """
    # escape harmful tags like <script> to prevent attacks like injections
    # bleach standard settings still allow tags like <b> to style text, harder rules could be enforced
    message_text = bleach.clean(message['message'])
    hashid = message['hash_id']

    new_message = ChatmessageIngame(
        message=message_text,
        author=message['user_id'],
        timestamp=datetime.utcnow(),
        game_hashid=hashid,
    )

    db.session.add(new_message)
    db.session.commit()

    author = (
        User.query.
        with_entities(User.username).
        filter_by(id=new_message.author).
        first_or_404()[0]
    )

    emit_data = {
        'author': author,
        'message': new_message.message,
        'author_id': new_message.author,
    }

    emit(
        'send_message',
        emit_data,
        room=hashid,
        broadcast=True,
    )


@socketio.on('broadcast_private_message', namespace='/private_messages')
def send_private_message(message):
    """Save and relay chat message in private chat.

    Args:
        message: Message sent by one player.
                 Contains message, author userID, receiver userID and game hashID.
    """
    # escape harmful tags like <script> to prevent attacks like injections
    # bleach standard settings still allow tags like <b> to style text, harder rules could be enforced
    message_text = bleach.clean(message['message'])
    receiver = message['receiver']
    new_message = Privatemessage(
        message=message_text,
        sender=current_user.id,
        receiver=receiver,
        timestamp=datetime.utcnow(),
    )

    sender_name = current_user.username
    receiver_name = (
        User.query.
        with_entities(User.username).
        filter_by(id=receiver).
        first_or_404()[0]
    )

    notification = Notification(user=receiver, message=message_text, author=sender_name, type='message')

    db.session.add(new_message)
    db.session.add(notification)
    db.session.commit()

    send_notification(receiver_name, message_text, sender_name, 'message')

    emit_data = {
        'message': message_text,
        'sender': current_user.id,
        'sender_name': sender_name,
        'receiver_name': receiver_name,
        'receiver': message['receiver'],
        'timestamp': f'{str(datetime.utcnow())}Z',
    }

    emit(
        'broadcast_private_message',
        emit_data,
        room=receiver_name,
        broadcast=True,
    )

    emit(
        'broadcast_private_message',
        emit_data,
        room=sender_name,
        broadcast=True,
    )
