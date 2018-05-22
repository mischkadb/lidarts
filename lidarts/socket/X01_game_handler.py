from flask import request
from flask_socketio import emit, join_room, leave_room
from lidarts import socketio
from lidarts.models import Game
from lidarts.socket.utils import process_score, current_turn_user_id


@socketio.on('connect', namespace='/game')
def connect():
    print('Client connected', request.sid)


@socketio.on('init', namespace='/game')
def init(message):
    game = Game.query.filter_by(hashid=message['hashid']).first_or_404()
    join_room(game.hashid)
    emit('score_response', {'p1_score': game.p1_score, 'p2_score': game.p2_score, 'p1_sets': game.p1_sets,
                            'p2_sets': game.p2_sets, 'p1_legs': game.p1_legs, 'p2_legs': game.p2_legs,
                            'p1_next_turn': game.p1_next_turn},
         room=game.hashid)


@socketio.on('init_waiting', namespace='/game')
def init_waiting(message):
    game = Game.query.filter_by(hashid=message['hashid']).first_or_404()
    join_room(game.hashid)


@socketio.on('start_game', namespace='/game')
def start_game(hashid):
    emit('start_game', room=hashid, broadcast=True, namespace='/game')


@socketio.on('send_score', namespace='/game')
def send_score(message):
    if not message['score'] or int(message['user_id']) != current_turn_user_id(message['hashid']):
        return
    hashid = message['hashid']
    score_value = int(message['score'])
    game = process_score(hashid, score_value)
    emit('score_response',
         {'p1_score': game.p1_score, 'p2_score': game.p2_score, 'p1_sets': game.p1_sets,
          'p2_sets': game.p2_sets, 'p1_legs': game.p1_legs, 'p2_legs': game.p2_legs,
          'p1_next_turn': game.p1_next_turn}, room=game.hashid, broadcast=True)
    if game.status == 'completed':
        emit('game_completed', room=game.hashid, broadcast=True)
        leave_room(game.hashid)


@socketio.on('disconnect', namespace='/game')
def disconnect():
    print('Client disconnected', request.sid)
