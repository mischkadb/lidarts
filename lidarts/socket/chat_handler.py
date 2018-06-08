from flask import request
from flask_socketio import emit
from lidarts import socketio, db
from lidarts.models import User, Chatmessage
from datetime import datetime, timedelta


def broadcast_online_players():
    online_players_dict = {}
    online_players = User.query.filter(User.last_seen > (datetime.utcnow() - timedelta(seconds=15))).all()
    for user in online_players:
        online_players_dict[user.id] = {'username': user.username, 'status': user.status}

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


@socketio.on('disconnect', namespace='/chat')
def disconnect():
    print('Client disconnected', request.sid)
