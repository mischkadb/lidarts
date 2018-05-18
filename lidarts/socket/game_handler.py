from flask import session, request, jsonify
from flask_socketio import emit
from lidarts import socketio, db
from lidarts.models import Game
import math


def player_to_dict(game, player1):
    player_dict = {
        'bo_legs': game.bo_legs,
        'bo_sets': game.bo_sets,
        'type': game.type,
        'completed': game.completed
    }
    if player1:
        player_dict['p_score'] = game.p1_score
        player_dict['p_legs'] = game.p1_legs
        player_dict['p_sets'] = game.p1_sets
    else:
        player_dict['p_score'] = game.p2_score
        player_dict['p_legs'] = game.p2_legs
        player_dict['p_sets'] = game.p2_sets
    return player_dict


def game_from_dict(game, player_dict):
    if game.p1_next_turn:
        game.p1_score = player_dict['p_score']
        game.p1_legs = player_dict['p_legs']
        game.p1_sets = player_dict['p_sets']
    else:
        game.p2_score = player_dict['p_score']
        game.p2_legs = player_dict['p_legs']
        game.p2_sets = player_dict['p_sets']
    game.completed = player_dict['completed']
    return game


def process_game_win(game):
    pass


def process_leg_win(player_dict):
    # draw not implemented
    legs_for_set = math.ceil(player_dict['bo_legs'] / 2)
    sets_for_match = math.ceil(player_dict['bo_sets'] / 2)
    player_dict['p_legs'] = (player_dict['p_legs'] + 1) % legs_for_set
    player_dict['p_score'] = player_dict['type']
    if player_dict['p_legs'] == 0:
        player_dict['p_sets'] += 1
        if player_dict['p_sets'] == sets_for_match:
            player_dict['completed'] = True
            player_dict['p_score'] = 0
    return player_dict


def process_score(hashid, score_value):
    game = Game.query.filter_by(hashid=hashid).first_or_404()
    if game.completed:
        return game
    player_dict = player_to_dict(game, game.p1_next_turn)

    if player_dict['p_score'] - score_value == 0:
        player_dict = process_leg_win(player_dict)
        if not player_dict['completed']:
            game.p1_score = game.type
            game.p2_score = game.type
    elif player_dict['p_score'] - score_value < 0:
        pass
    else:
        player_dict['p_score'] -= score_value

    game = game_from_dict(game, player_dict)
    if game.completed:
        process_game_win(game)
    else:
        game.p1_next_turn = not game.p1_next_turn
    db.session.commit()
    return game


@socketio.on('send_score', namespace='/game')
def send_score(message):
    if not message['score']:
        return
    hashid = message['hashid']
    score_value = int(message['score'])
    game = process_score(hashid, score_value)
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('score_response',
         {'p1_score': game.p1_score, 'p2_score': game.p2_score, 'p1_sets': game.p1_sets,
          'p2_sets': game.p2_sets, 'p1_legs': game.p1_legs, 'p2_legs': game.p2_legs}, broadcast=True)
    if game.completed:
        print('emit completed')
        emit('game_completed', broadcast=True)


@socketio.on('connect', namespace='/game')
def connect():
    print('Client connected', request.sid)


@socketio.on('init', namespace='/game')
def init(message):
    game = Game.query.filter_by(hashid=message['hashid']).first_or_404()
    emit('score_response', {'p1_score': game.p1_score, 'p2_score': game.p2_score, 'p1_sets': game.p1_sets,
                            'p2_sets': game.p2_sets, 'p1_legs': game.p1_legs, 'p2_legs': game.p2_legs})


@socketio.on('disconnect', namespace='/game')
def disconnect():
    print('Client disconnected', request.sid)
