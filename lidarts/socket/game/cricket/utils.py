from flask import request
from flask_socketio import emit
from flask_login import current_user
from lidarts import db, avatars, socketio
from lidarts.game.utils import cricket_leg_default
from lidarts.socket.utils import broadcast_game_completed
from lidarts.models import Game, Tournament, User, UserSettings, UserStatistic, WebcamSettings
import math
import json
from datetime import datetime, timedelta
from sqlalchemy import or_


def player1_started_leg(leg):
    # player 1 started leg if player 1 threw more darts (no break)
    # or player 1 lost the leg and threw the same amount of darts (break)
    return len(leg['1']['scores']) > len(leg['2']['scores']) \
           or (len(leg['1']['scores']) == len(leg['2']['scores'])
               and leg['1']['points'] < leg['2']['points'])


def player_to_dict(game, player1):
    player_dict = {
        'bo_legs': game.bo_legs,
        'bo_sets': game.bo_sets,
        'two_clear_legs': game.two_clear_legs,
        'two_clear_legs_wc_mode': game.two_clear_legs_wc_mode,
        'status': game.status,
    }
    if player1:
        player_dict['p_score'] = game.p1_score
        player_dict['o_score'] = game.p2_score
        player_dict['p_legs'] = game.p1_legs
        player_dict['p_sets'] = game.p1_sets
        player_dict['o_legs'] = game.p2_legs
        player_dict['o_sets'] = game.p2_sets
    else:
        player_dict['p_score'] = game.p2_score
        player_dict['o_score'] = game.p1_score
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
    game.status = player_dict['status']
    return game


def process_leg_win(player_dict, match_json, current_values):
    # check if draws are possible
    set_draw_possible = (player_dict['bo_sets'] % 2) == 0
    leg_draw_possible = (player_dict['bo_legs'] % 2) == 0

    # amount of legs/sets needed to win
    legs_for_set = (player_dict['bo_legs'] / 2) + 1 if leg_draw_possible else math.ceil(player_dict['bo_legs'] / 2)
    sets_for_match = (player_dict['bo_sets'] / 2) + 1 if set_draw_possible else math.ceil(player_dict['bo_sets'] / 2)

    # leg count increase with check for set win
    if player_dict['two_clear_legs']:
        player_dict['p_legs'] += 1
    # world champs mode: two clear legs only in last set. sudden death at 5:5  legs
    elif player_dict['two_clear_legs_wc_mode'] and player_dict['p_sets'] == player_dict['o_sets'] == (sets_for_match - 1):
        player_dict['p_legs'] += 1
    else:
        player_dict['p_legs'] = (player_dict['p_legs'] + 1) % legs_for_set
    # reset score to default value
    player_dict['p_score'] = 0

    # check if player won set
    if (
        player_dict['p_legs'] == 0 
        or (
            player_dict['two_clear_legs']
            and player_dict['p_legs'] >= legs_for_set 
            and player_dict['p_legs'] >= player_dict['o_legs'] + 2
        )
        or (
            # world champs mode: two clear legs only in last set. sudden death at 5:5 legs
            player_dict['two_clear_legs_wc_mode']
            and player_dict['p_legs'] >= legs_for_set
            and player_dict['p_sets'] == player_dict['o_sets'] == (sets_for_match - 1)
            and ((
                player_dict['p_legs'] >= player_dict['o_legs'] + 2
            ) or (
                # edge case: wc mode and large bo_legs: opponent might have more legs than 5
                player_dict['p_legs'] > player_dict['o_legs'] and player_dict['o_legs'] >= 5
            ))
        )
    ):
        player_dict['p_sets'] += 1

        # check if player won match or match drawn
        if player_dict['p_sets'] == sets_for_match or \
                (set_draw_possible and (player_dict['p_sets'] == player_dict['o_sets'] == (player_dict['bo_sets'] / 2))):
            # leg score is needed if best of 1 set
            if player_dict['bo_sets'] == 1 and player_dict['p_legs'] == 0:
                player_dict['p_legs'] = math.ceil((player_dict['bo_legs'] + 0.5) / 2)
            player_dict['status'] = 'completed'
            player_dict['p_score'] = 0  # end score 0 looks nicer
        else:  # match not over, new set
            player_dict['p_legs'] = 0
            player_dict['o_legs'] = 0
            current_values['set'] = str(int(current_values['set']) + 1)
            current_values['leg'] = '1'
            match_json[current_values['set']] = {current_values['leg']: cricket_leg_default.copy()}

    else:  # no new set unless drawn
        # check for drawn set
        if leg_draw_possible and (player_dict['p_legs'] == player_dict['o_legs'] == (player_dict['bo_legs'] / 2)):
            player_dict['p_sets'] += 1
            player_dict['o_sets'] += 1
            # check if a player won the match
            if player_dict['p_sets'] == sets_for_match or player_dict['o_sets'] == sets_for_match:
                player_dict['status'] = 'completed'
                player_dict['p_score'] = 0
            # check if match is drawn - redundant atm, could be merged with game win
            elif set_draw_possible and (player_dict['p_sets'] == player_dict['o_sets'] == (player_dict['bo_sets'] / 2)):
                player_dict['status'] = 'completed'
                player_dict['p_score'] = 0
            # no one won the match, new set
            else:
                player_dict['p_legs'] = 0
                player_dict['o_legs'] = 0
                current_values['set'] = str(int(current_values['set']) + 2)  # + 2 because both players won a set
                current_values['leg'] = '1'
                match_json[current_values['set']] = {current_values['leg']: cricket_leg_default.copy()}
        else:  # no draw, just new leg
            current_values['leg'] = str(int(current_values['leg']) + 1)
            match_json[current_values['set']][current_values['leg']] = cricket_leg_default.copy()

    return player_dict, match_json, current_values


def process_score(game, score_value):
    match_json = json.loads(game.match_json)

    if game.status != 'started':
        return game

    current_values = {
        'set': str(game.p1_sets + game.p2_sets + 1),
        'leg': str(game.p1_legs + game.p2_legs + 1),
        'player': '1' if game.p1_next_turn is True else '2',
        'opponent': '2' if game.p1_next_turn is True else '1',
    }
    player_dict = player_to_dict(game, game.p1_next_turn)
    new_leg_starter = 0  # used for leg starting player

    current_player_json = match_json[current_values['set']][current_values['leg']][current_values['player']]
    opponent_json = match_json[current_values['set']][current_values['leg']][current_values['opponent']]
    scores = current_player_json['scores']
    fields = current_player_json['fields']
    points = current_player_json['points']
    opponent_fields = opponent_json['fields']
    opponent_scores = opponent_json['scores']

    if score_value > 0:
        if 0 < score_value <= 25:
            field = str(score_value)
            marks = 1
        elif 25 < score_value <= 40 or score_value == 50:
            field = str(score_value // 2)
            marks = 2
        else:
            field = str(score_value // 3)
            marks = 3

        if fields[field]['marks'] + marks > 3:
            marks_to_score = fields[field]['marks'] + marks - 3
            fields[field]['marks'] = 3
        else:
            marks_to_score = 0
            fields[field]['marks'] += marks
        
        # check for closed field
        if opponent_fields[field]['marks'] == 3:
            score_value = (score_value // marks) * (marks - marks_to_score)
            marks_to_score = 0

        fields[field]['score'] += marks_to_score * int(field)
        points += marks_to_score * int(field)

    if scores and len(scores[-1]) < 3:
        scores[-1].append(score_value)
    else:
        scores.append([score_value])
        game.undo_possible = True

    if len(scores[-1]) == 3:
        game.confirmation_needed = True

    player_dict['p_score'] = points
    match_json[current_values['set']][current_values['leg']][current_values['player']]['scores'] = scores
    match_json[current_values['set']][current_values['leg']][current_values['player']]['fields'] = fields
    match_json[current_values['set']][current_values['leg']][current_values['player']]['points'] = points

    # check if leg was won
    all_fields_closed = True
    for field in fields:
        if fields[field]['marks'] < 3:
            all_fields_closed = False
            break

    if all_fields_closed and player_dict['p_score'] >= player_dict['o_score']:
        # check who begins next leg
        new_leg_starter = '2' \
            if player1_started_leg(match_json[current_values['set']][current_values['leg']]) else '1'
        current_set = current_values['set']

        # check for won sets, won match, update scores etc.
        player_dict, match_json, current_values = process_leg_win(player_dict, match_json, current_values)

        # set mode only: new sets are started alternately, need to recheck leg starter)
        if current_values['set'] > current_set and len(match_json[current_set]) % 2 == 0:
            new_leg_starter = '2' if new_leg_starter == '1' else '1'

        # reset player scores to default
        if not player_dict['status'] == 'completed':
            game.p1_score = 0
            game.p2_score = 0
            game.undo_possible = False
            game.confirmation_needed = False

    # save everything back into the model object
    game = game_from_dict(game, player_dict)
    game.match_json = json.dumps(match_json)

    if game.status == 'completed':
        game.end = datetime.utcnow()
        if not game.opponent_type.startswith('computer'):
            broadcast_game_completed(game)
    # new leg
    elif new_leg_starter:
        game.p1_next_turn = True if new_leg_starter == '1' else False
        
    db.session.commit()
    return game
