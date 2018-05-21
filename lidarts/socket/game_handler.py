from flask import session, request, jsonify
from flask_socketio import emit, join_room, leave_room
from lidarts import socketio, db
from lidarts.models import Game
import math
from datetime import datetime
import json


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
        player_dict['o_legs'] = game.p2_legs
        player_dict['o_sets'] = game.p2_sets
    else:
        player_dict['p_score'] = game.p2_score
        player_dict['p_legs'] = game.p2_legs
        player_dict['p_sets'] = game.p2_sets
        player_dict['o_legs'] = game.p1_legs
        player_dict['o_sets'] = game.p1_sets
    return player_dict


def game_from_dict(game, player_dict):
    if game.p1_next_turn:
        game.p1_score = player_dict['p_score']
        game.p1_legs = player_dict['p_legs']
        game.p1_sets = player_dict['p_sets']
        game.p2_legs = player_dict['o_legs']
        game.p2_sets = player_dict['o_sets']
    else:
        game.p2_score = player_dict['p_score']
        game.p2_legs = player_dict['p_legs']
        game.p2_sets = player_dict['p_sets']
        game.p1_legs = player_dict['o_legs']
        game.p1_sets = player_dict['o_sets']
    game.completed = player_dict['completed']
    return game


def process_leg_win(player_dict, match_json, current_values):
    set_draw_possible = (player_dict['bo_sets'] % 2) == 0
    leg_draw_possible = (player_dict['bo_legs'] % 2) == 0
    legs_for_set = (player_dict['bo_legs'] / 2) + 1 if leg_draw_possible else math.ceil(player_dict['bo_legs'] / 2)
    sets_for_match = (player_dict['bo_sets'] / 2) + 1 if set_draw_possible else math.ceil(player_dict['bo_sets'] / 2)
    player_dict['p_legs'] = (player_dict['p_legs'] + 1) % legs_for_set
    player_dict['p_score'] = player_dict['type']
    # check if player won set
    if player_dict['p_legs'] == 0:
        player_dict['p_sets'] += 1
        # check if player won match
        if player_dict['p_sets'] == sets_for_match:
            # leg score is needed if best of 1 set
            if player_dict['bo_sets'] == 1:
                player_dict['p_legs'] = math.ceil(player_dict['bo_legs'] / 2)
            player_dict['completed'] = True
            player_dict['p_score'] = 0  # end score 0 looks nicer
        else:  # match not over, new set
            player_dict['o_legs'] = 0
            current_values['set'] = str(int(current_values['set']) + 1)
            current_values['leg'] = '1'
            match_json[current_values['set']] = {current_values['leg']: {'1': [], '2': []}}
    else:  # no new set unless drawn
        # check for drawn set
        if leg_draw_possible and (player_dict['p_legs'] == player_dict['o_legs'] == (player_dict['bo_legs'] / 2)):
            player_dict['p_sets'] += 1
            player_dict['o_sets'] += 1
            # check if a player won the match
            if player_dict['p_sets'] == sets_for_match or player_dict['o_sets'] == sets_for_match:
                player_dict['completed'] = True
                player_dict['p_score'] = 0
            # check if match is drawn - redundant atm, could be merged with game win
            elif set_draw_possible and (player_dict['p_sets'] == player_dict['o_sets'] == (player_dict['bo_sets'] / 2)):
                player_dict['completed'] = True
                player_dict['p_score'] = 0
            # no one won the match, new set
            else:
                player_dict['p_legs'] = 0
                player_dict['o_legs'] = 0
                current_values['set'] = str(int(current_values['set']) + 2)  # + 2 because both players won a set
                current_values['leg'] = '1'
                match_json[current_values['set']] = {current_values['leg']: {'1': [], '2': []}}
        else:  # no draw, just new leg
            current_values['leg'] = str(int(current_values['leg']) + 1)
            match_json[current_values['set']][current_values['leg']] = {'1': [], '2': []}

    return player_dict, match_json, current_values


def process_score(hashid, score_value):
    game = Game.query.filter_by(hashid=hashid).first_or_404()
    match_json = json.loads(game.match_json)
    if game.completed:
        return game
    current_values = {
        'set': str(game.p1_sets + game.p2_sets + 1),
        'leg': str(game.p1_legs + game.p2_legs + 1),
        'player': '1' if game.p1_next_turn is True else '2'
    }
    player_dict = player_to_dict(game, game.p1_next_turn)
    if player_dict['p_score'] - score_value == 0:
        match_json[current_values['set']][current_values['leg']][current_values['player']].append(score_value)
        player_dict, match_json, current_values = process_leg_win(player_dict, match_json, current_values)
        if not player_dict['completed']:
            game.p1_score = game.type
            game.p2_score = game.type
    elif player_dict['p_score'] - score_value < 0:
        match_json[current_values['set']][current_values['leg']][current_values['player']].append(0)
    # Double/Master out: score cannot drop to 1
    elif game.out_mode in ['do', 'mo'] and player_dict['p_score'] - score_value == 1:
        match_json[current_values['set']][current_values['leg']][current_values['player']].append(0)
    else:
        player_dict['p_score'] -= score_value
        match_json[current_values['set']][current_values['leg']][current_values['player']].append(score_value)

    game = game_from_dict(game, player_dict)
    game.match_json = json.dumps(match_json)
    if game.completed:
        game.end = datetime.now()
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
    emit('score_response',
         {'p1_score': game.p1_score, 'p2_score': game.p2_score, 'p1_sets': game.p1_sets,
          'p2_sets': game.p2_sets, 'p1_legs': game.p1_legs, 'p2_legs': game.p2_legs}, room=game.hashid, broadcast=True)
    if game.completed:
        emit('game_completed', room=game.hashid, broadcast=True)
        leave_room(game.hashid)


@socketio.on('connect', namespace='/game')
def connect():
    print('Client connected', request.sid)


@socketio.on('init', namespace='/game')
def init(message):
    game = Game.query.filter_by(hashid=message['hashid']).first_or_404()
    join_room(game.hashid)
    emit('score_response', {'p1_score': game.p1_score, 'p2_score': game.p2_score, 'p1_sets': game.p1_sets,
                            'p2_sets': game.p2_sets, 'p1_legs': game.p1_legs, 'p2_legs': game.p2_legs},
         room=game.hashid)


@socketio.on('disconnect', namespace='/game')
def disconnect():
    print('Client disconnected', request.sid)
