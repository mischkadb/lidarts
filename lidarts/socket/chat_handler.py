from flask import request
from flask_socketio import emit, join_room
from flask_login import current_user
from lidarts import socketio, db
from lidarts.models import User, Chatmessage, Privatemessage
from datetime import datetime, timedelta


def broadcast_online_players():
    online_players_dict = {}
    online_players = User.query.filter(User.last_seen > (datetime.utcnow() - timedelta(seconds=15))).all()
    for user in online_players:
        status = user.status
        if user.last_seen_ingame and user.last_seen_ingame > (datetime.utcnow() - timedelta(seconds=10)):
            status = 'playing'
        online_players_dict[user.id] = {'username': user.username, 'status': status}

    emit('send_online_players', online_players_dict, broadcast=True, namespace='/chat')


def broadcast_new_game(game):
    p1_name, = User.query.with_entities(User.username).filter_by(id=game.player1).first_or_404()
    p2_name, = User.query.with_entities(User.username).filter_by(id=game.player2).first_or_404()

    emit('send_system_message_new_game', {'hashid': game.hashid, 'p1_name': p1_name, 'p2_name': p2_name},
         broadcast=True, namespace='/chat')


def broadcast_game_completed(game):
    p1_name, = User.query.with_entities(User.username).filter_by(id=game.player1).first_or_404()
    p2_name, = User.query.with_entities(User.username).filter_by(id=game.player2).first_or_404()

    if game.bo_sets > 1:
        p1_score = game.p1_sets
        p2_score = game.p2_sets
    else:
        p1_score = game.p1_legs
        p2_score = game.p2_legs

    emit('send_system_message_game_completed', {'hashid': game.hashid, 'p1_name': p1_name, 'p2_name': p2_name,
                                                'p1_score': p1_score, 'p2_score': p2_score},
         broadcast=True, namespace='/chat')


@socketio.on('connect', namespace='/chat')
def connect():
    print('Client connected', request.sid)
    broadcast_online_players()


@socketio.on('broadcast_chat_message', namespace='/chat')
def broadcast_chat_message(message):
    new_message = Chatmessage(message=message['message'], author=message['user_id'], timestamp=datetime.utcnow())
    db.session.add(new_message)
    db.session.commit()

    author = User.query.with_entities(User.username) \
        .filter_by(id=new_message.author).first_or_404()[0]

    emit('send_message', {'author': author, 'message': new_message.message,
                          'timestamp': str(new_message.timestamp) + 'Z'},
         broadcast=True)


@socketio.on('connect', namespace='/private_messages')
def connect():
    print('Client connected', request.sid)
    if current_user.is_authenticated:
        join_room(current_user.username)


@socketio.on('broadcast_private_message', namespace='/private_messages')
def send_private_message(message):
    receiver, = User.query.with_entities(User.id).filter_by(username=message['receiver']).first_or_404()
    new_message = Privatemessage(message=message['message'], sender=current_user.id,
                                 receiver=receiver, timestamp=datetime.utcnow())
    db.session.add(new_message)
    db.session.commit()

    sender_name = current_user.username
    receiver_name = User.query.with_entities(User.username).filter_by(id=receiver).first_or_404()[0]

    emit('broadcast_private_message', dict(message=message['message'], sender=current_user.id,
                                           sender_name=sender_name, receiver_name=receiver_name,
                                           receiver=message['receiver'], timestamp=str(datetime.utcnow()) + 'Z'),
         room=receiver_name, broadcast=True)

    emit('broadcast_private_message', dict(message=message['message'], sender=current_user.id,
                                           sender_name=sender_name, receiver_name=receiver_name,
                                           receiver=message['receiver'], timestamp=str(datetime.utcnow()) + 'Z'),
         room=sender_name, broadcast=True)


@socketio.on('disconnect', namespace='/chat')
def disconnect():
    print('Client disconnected', request.sid)
