# -*- coding: utf-8 -*-

"""Game chat socket handler.

Saves and relays game chat messages.
"""

from datetime import datetime

from flask_socketio import emit, join_room

from lidarts import db, socketio
from lidarts.models import ChatmessageIngame, Game, User
from lidarts.socket.chat.chat_utils import clean_message


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
    message_text = clean_message(message['message'])
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
