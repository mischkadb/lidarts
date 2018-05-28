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
    # stats
    p1_leg_avg = round(sum(p1_current_leg) / len(p1_current_leg), 2) if len(p1_current_leg) else 0
    p2_leg_avg = round(sum(p2_current_leg) / len(p2_current_leg), 2) if len(p2_current_leg) else 0

    p1_180 = 0
    p2_180 = 0
    p1_140 = 0
    p2_140 = 0
    p1_100 = 0
    p2_100 = 0
    p1_scores = []
    p2_scores = []
    p1_first9_scores = []
    p2_first9_scores = []
    p1_high_finish = 0
    p2_high_finish = 0
    p1_short_leg = 0
    p2_short_leg = 0

    for set in match_json:
        for leg in match_json[set]:
            if sum(match_json[set][leg]['1']) == game.type:
                p1_short_leg = len(match_json[set][leg]['1'])*3 if p1_short_leg == 0 else p1_short_leg
                p1_short_leg = len(match_json[set][leg]['1'])*3 \
                    if len(match_json[set][leg]['1']) < p1_short_leg else p1_short_leg
                p1_high_finish = match_json[set][leg]['1'][-1] \
                    if match_json[set][leg]['1'][-1] > p1_high_finish else p1_high_finish

            if sum(match_json[set][leg]['2']) == game.type:
                p2_short_leg = len(match_json[set][leg]['2'])*3 if p2_short_leg == 0 else p2_short_leg
                p2_short_leg = len(match_json[set][leg]['2'])*3 \
                    if len(match_json[set][leg]['2']) < p2_short_leg else p2_short_leg
                p2_high_finish = match_json[set][leg]['2'][-1] \
                    if match_json[set][leg]['2'][-1] > p2_high_finish else p2_high_finish

            for i, score in enumerate(match_json[set][leg]['1']):
                p1_scores.append(score)
                if i <= 3:
                    p1_first9_scores.append(score)
                if score == 180:
                    p1_180 += 1
                elif score >= 140:
                    p1_140 += 1
                elif score >= 100:
                    p1_100 += 1

            for i, score in enumerate(match_json[set][leg]['2']):
                p2_scores.append(score)
                if i <= 3:
                    p2_first9_scores.append(score)
                if score == 180:
                    p2_180 += 1
                elif score >= 140:
                    p2_140 += 1
                elif score >= 100:
                    p2_100 += 1

    p1_match_avg = round(sum(p1_scores) / len(p1_scores), 2) if p1_scores else 0
    p2_match_avg = round(sum(p2_scores) / len(p2_scores), 2) if p2_scores else 0
    p1_first9_avg = round(sum(p1_first9_scores)/len(p1_first9_scores),2) if p1_first9_scores else 0
    p2_first9_avg = round(sum(p2_first9_scores)/len(p2_first9_scores), 2) if p2_first9_scores else 0

    emit('score_response',
         {'p1_score': game.p1_score, 'p2_score': game.p2_score, 'p1_sets': game.p1_sets,
          'p2_sets': game.p2_sets, 'p1_legs': game.p1_legs, 'p2_legs': game.p2_legs,
          'p1_next_turn': game.p1_next_turn, 'p1_current_leg': p1_current_leg,
          'p2_current_leg': p2_current_leg, 'old_score': old_score,
          'p1_leg_avg': p1_leg_avg, 'p2_leg_avg': p2_leg_avg,
          'p1_match_avg': p1_match_avg, 'p2_match_avg': p2_match_avg,
          'p1_first9_avg': p1_first9_avg, 'p2_first9_avg': p2_first9_avg,
          'p1_100': p1_100, 'p2_100': p2_100,
          'p1_140': p1_140, 'p2_140': p2_140,
          'p1_180': p1_180, 'p2_180': p2_180,
          #'p1_doubles': p1_doubles, 'p2_doubles': p2_doubles,
          'p1_high_finish': p1_high_finish, 'p2_high_finish': p2_high_finish,
          'p1_short_leg': p1_short_leg, 'p2_short_leg': p2_short_leg
          },

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
                                'type': game.type, 'p1_sets': game.p1_sets,
                                'p2_sets': game.p2_sets, 'p1_legs': game.p1_legs, 'p2_legs': game.p2_legs},
             room=game.hashid, broadcast=True)
        leave_room(game.hashid)

    if old_set_count < len(match_json) or old_leg_count < len(match_json[str(len(match_json))]):
        if len(match_json[str(len(match_json))]) == 1:  # new set
            last_set = match_json[str(len(match_json)-1)]
            last_leg = last_set[str(len(last_set))]
        else:  # no new set
            last_set = match_json[str(len(match_json))]
            last_leg = last_set[str(len(last_set)-1)]
        p1_last_leg = last_leg['1']
        p2_last_leg = last_leg['2']
        p1_won = sum(p1_last_leg) == game.type
        emit('game_shot', {'p1_last_leg': p1_last_leg, 'p2_last_leg': p2_last_leg, 'p1_won': p1_won,
                           'type': game.type, 'p1_sets': game.p1_sets,
                           'p2_sets': game.p2_sets, 'p1_legs': game.p1_legs, 'p2_legs': game.p2_legs},
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
