from flask import request
from flask_socketio import emit, join_room, leave_room
from lidarts import socketio
from lidarts.models import Game
from lidarts.socket.utils import process_score, current_turn_user_id
import json


def send_score_response(game, old_score=0, broadcast=False):
    match_json = json.loads(game.match_json)
    current_set = str(len(match_json))
    current_leg = str(len(match_json[str(len(match_json))]))
    p1_current_leg = match_json[current_set][current_leg]['1']
    p2_current_leg = match_json[current_set][current_leg]['2']
    emit('score_response',
         {'p1_score': game.p1_score, 'p2_score': game.p2_score, 'p1_sets': game.p1_sets,
          'p2_sets': game.p2_sets, 'p1_legs': game.p1_legs, 'p2_legs': game.p2_legs,
          'p1_next_turn': game.p1_next_turn, 'p1_current_leg': p1_current_leg,
          'p2_current_leg': p2_current_leg, 'old_score': old_score},
         room=game.hashid, broadcast=broadcast)


@socketio.on('connect', namespace='/game')
def connect():
    print('Client connected', request.sid)


@socketio.on('init', namespace='/game')
def init(message):
    game = Game.query.filter_by(hashid=message['hashid']).first_or_404()
    join_room(game.hashid)
    send_score_response(game, broadcast=False)


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
    game = Game.query.filter_by(hashid=hashid).first()
    match_json = json.loads(game.match_json)
    old_score = game.p1_score if game.p1_next_turn else game.p2_score
    old_set_count = len(match_json)
    old_leg_count = len(match_json[str(len(match_json))])
    game = process_score(hashid, score_value)
    match_json = json.loads(game.match_json)

    if game.status == 'completed':
        last_set = match_json[str(len(match_json))]
        last_leg = last_set[str(len(last_set))]
        p1_last_leg = last_leg['1']
        p2_last_leg = last_leg['2']
        p1_won = sum(p1_last_leg) == game.type
        emit('game_completed', {'p1_last_leg': p1_last_leg, 'p2_last_leg': p2_last_leg, 'p1_won': p1_won,
                                'type': game.type},
             room=game.hashid, broadcast=True)
        leave_room(game.hashid)

    if old_set_count < len(match_json) or old_leg_count < len(match_json[str(len(match_json))]):
        if len(match_json[str(len(match_json))]) == 1:
            last_set = match_json[str(len(match_json)-1)]
            last_leg = last_set[str(len(last_set))]
        else:
            last_set = match_json[str(len(match_json))]
            last_leg = last_set[str(len(last_set)-1)]
        p1_last_leg = last_leg['1']
        p2_last_leg = last_leg['2']
        p1_won = sum(p1_last_leg) == game.type
        emit('game_shot', {'p1_last_leg': p1_last_leg, 'p2_last_leg': p2_last_leg, 'p1_won': p1_won,
                           'type': game.type},
             room=game.hashid, broadcast=True)
    else:
        send_score_response(game, old_score, broadcast=True)


@socketio.on('get_score_after_leg_win', namespace='/game')
def get_score_after_leg_win(message):
    if not message['hashid']:
        return
    hashid = message['hashid']
    game = Game.query.filter_by(hashid=hashid).first()
    send_score_response(game, broadcast=True)
    if game.status == 'completed':
        emit('game_completed', room=game.hashid, broadcast=True)
        leave_room(game.hashid)


@socketio.on('disconnect', namespace='/game')
def disconnect():
    print('Client disconnected', request.sid)
