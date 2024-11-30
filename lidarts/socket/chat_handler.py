from flask import request
from flask_socketio import emit, join_room
from flask_login import current_user
from lidarts import socketio, db
from lidarts.models import User, Chatmessage, Privatemessage, Notification, Game, CricketGame, ChatmessageIngame, UserStatistic, UserSettings
from lidarts.socket.utils import authenticated_only, broadcast_online_players, send_notification
from lidarts.utils.linker import linker
from datetime import datetime
import bleach


@socketio.on('connect', namespace='/chat')
@authenticated_only
def connect_chat():
    # print('Client connected', request.sid)
    # broadcast_online_players(broadcast=False)
    pass


@socketio.on('init', namespace='/chat')
@authenticated_only
def init(message):
    room = message['hashid'] if 'hashid' in message else 'public_chat'
    join_room(room)
    broadcast_online_players(broadcast=False, room=room)


@socketio.on('broadcast_chat_message', namespace='/chat')
@authenticated_only
def broadcast_chat_message(message):
    room = message['hashid'] if 'hashid' in message else 'public_chat'
    tournament_hashid = message['hashid'] if 'hashid' in message else None

    message['message'] = bleach.clean(message['message'])
    message['message'] = linker.linkify(message['message'])
    new_message = Chatmessage(
        message=message['message'],
        author=message['user_id'],
        timestamp=datetime.utcnow(),
        tournament_hashid=tournament_hashid,    
    )
    db.session.add(new_message)
    user_statistic = UserStatistic.query.filter_by(user=message['user_id']).first()
    if not user_statistic:
        user_statistic = UserStatistic(user=message['user_id'], average=0, doubles=0)
        db.session.add(user_statistic)
    db.session.commit()

    statistics = {'average': user_statistic.average, 'doubles': user_statistic.doubles}

    country = UserSettings.query.with_entities(UserSettings.country).filter_by(user=message['user_id']).first()
    if country:
        country = country[0]
    else:
        country = UserSettings(user=message['user_id'])
        db.session.add(country)
        db.session.commit()
        country = None

    author = User.query.with_entities(User.username) \
        .filter_by(id=new_message.author).first_or_404()[0]

    emit(
        'send_message',
        {
            'author': author,
            'message': new_message.message,
            'statistics': statistics,
            'timestamp': str(new_message.timestamp) + 'Z',
            'country': country,
        },
        room=room,
    )


@socketio.on('connect', namespace='/private_messages')
@authenticated_only
def connect_private_messages():
    # print('Client connected', request.sid)
    if current_user.is_authenticated:
        join_room(current_user.username)


@socketio.on('init', namespace='/game_chat')
@authenticated_only
def init(message):
    game = Game.query.filter_by(hashid=message['hashid']).first()
    if not game:
        game = CricketGame.query.filter_by(hashid=message['hashid']).first_or_404()
    join_room(game.hashid)


@socketio.on('broadcast_game_chat_message', namespace='/game_chat')
@authenticated_only
def send_game_chat_message(message):
    if 'message' not in message or 'user_id' not in message or 'hash_id' not in message:
        return
    message['message'] = bleach.clean(message['message'])
    message['message'] = linker.linkify(message['message'])
    hashid = message['hash_id']
    new_message = ChatmessageIngame(message=message['message'], author=current_user.id,
                                    timestamp=datetime.utcnow(), game_hashid=hashid)
    db.session.add(new_message)
    db.session.commit()

    author = User.query.with_entities(User.username) \
        .filter_by(id=new_message.author).first_or_404()[0]

    emit('send_message', {'author': author, 'message': new_message.message, 'author_id': new_message.author},
         room=hashid, broadcast=True)


@socketio.on('broadcast_private_message', namespace='/private_messages')
@authenticated_only
def send_private_message(message):
    message['message'] = bleach.clean(message['message'])
    message['message'] = linker.linkify(message['message'])
    receiver = message['receiver']

    receiver_settings = UserSettings.query.filter_by(user=receiver).first()
    if receiver_settings and not receiver_settings.allow_private_messages:
        emit('receiver_PMs_disabled', room=request.sid)
        return

    new_message = Privatemessage(message=message['message'], sender=current_user.id,
                                 receiver=receiver, timestamp=datetime.utcnow())

    sender_name = current_user.username
    receiver_name = User.query.with_entities(User.username).filter_by(id=receiver).first_or_404()[0]

    notification = Notification(user=receiver, message=message['message'], author=sender_name, type='message')

    db.session.add(new_message)
    db.session.add(notification)
    db.session.commit()

    send_notification(receiver_name, message['message'], sender_name, 'message')

    emit('broadcast_private_message', dict(message=message['message'], sender=current_user.id,
                                           sender_name=sender_name, receiver_name=receiver_name,
                                           receiver=message['receiver'], timestamp=str(datetime.utcnow()) + 'Z'),
         room=receiver_name, broadcast=True)

    emit('broadcast_private_message', dict(message=message['message'], sender=current_user.id,
                                           sender_name=sender_name, receiver_name=receiver_name,
                                           receiver=message['receiver'], timestamp=str(datetime.utcnow()) + 'Z'),
         room=sender_name, broadcast=True)


@socketio.on('disconnect', namespace='/chat')
@authenticated_only
def disconnect():
    # print('Client disconnected', request.sid)
    pass

