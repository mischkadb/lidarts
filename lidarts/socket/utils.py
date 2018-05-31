from lidarts import db
from lidarts.models import Game
from lidarts.socket.chat_handler import broadcast_game_completed
import math
import json
from datetime import datetime


def player1_started_leg(leg):
    # player 1 started leg if player 1 threw more darts (no break)
    # or player 1 lost the leg and threw the same amount of darts (break)
    return len(leg['1']) > len(leg['2']) or (len(leg['1']) == len(leg['2']) and sum(leg['1']) < sum(leg['2']))


def player_to_dict(game, player1):
    player_dict = {
        'bo_legs': game.bo_legs,
        'bo_sets': game.bo_sets,
        'type': game.type,
        'status': game.status
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
    player_dict['p_legs'] = (player_dict['p_legs'] + 1) % legs_for_set
    # reset score to default value
    player_dict['p_score'] = player_dict['type']

    # check if player won set
    if player_dict['p_legs'] == 0:
        player_dict['p_sets'] += 1
        # check if player won match
        if player_dict['p_sets'] == sets_for_match:
            # leg score is needed if best of 1 set
            if player_dict['bo_sets'] == 1:
                player_dict['p_legs'] = math.ceil(player_dict['bo_legs'] / 2)
            player_dict['status'] = 'completed'
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
                match_json[current_values['set']] = {current_values['leg']: {'1': [], '2': []}}
        else:  # no draw, just new leg
            current_values['leg'] = str(int(current_values['leg']) + 1)
            match_json[current_values['set']][current_values['leg']] = {'1': [], '2': []}

    return player_dict, match_json, current_values


def process_score(hashid, score_value):
    game = Game.query.filter_by(hashid=hashid).first_or_404()
    match_json = json.loads(game.match_json)

    if game.status != 'started':
        return game

    current_values = {
        'set': str(game.p1_sets + game.p2_sets + 1),
        'leg': str(game.p1_legs + game.p2_legs + 1),
        'player': '1' if game.p1_next_turn is True else '2'
    }
    player_dict = player_to_dict(game, game.p1_next_turn)
    new_leg_starter = 0  # used for leg starting player

    # check if leg was won
    if player_dict['p_score'] - score_value == 0:
        # add thrown score to match json object
        match_json[current_values['set']][current_values['leg']][current_values['player']].append(score_value)

        # check who begins next leg
        new_leg_starter = '2'  \
            if player1_started_leg(match_json[current_values['set']][current_values['leg']]) else '1'

        # check for won sets, won match, update scores etc.
        player_dict, match_json, current_values = process_leg_win(player_dict, match_json, current_values)

        # reset player scores to default
        if not player_dict['status'] == 'completed':
            game.p1_score = game.type
            game.p2_score = game.type
    # check if busted
    elif player_dict['p_score'] - score_value < 0:
        match_json[current_values['set']][current_values['leg']][current_values['player']].append(0)
    # Double/Master out: score cannot drop to 1
    elif game.out_mode in ['do', 'mo'] and player_dict['p_score'] - score_value == 1:
        match_json[current_values['set']][current_values['leg']][current_values['player']].append(0)
    # nothing special happened, just score
    else:
        player_dict['p_score'] -= score_value
        match_json[current_values['set']][current_values['leg']][current_values['player']].append(score_value)

    # save everything back into the model object
    game = game_from_dict(game, player_dict)
    game.match_json = json.dumps(match_json)

    if game.status == 'completed':
        game.end = datetime.now()
        broadcast_game_completed(game)
    # new leg
    elif new_leg_starter:
        game.p1_next_turn = True if new_leg_starter == '1' else False
    # no new leg, other player's turn
    else:
        game.p1_next_turn = not game.p1_next_turn
    db.session.commit()
    return game


def current_turn_user_id(hashid):
    game = Game.query.filter_by(hashid=hashid).first_or_404()
    return game.player1 if game.p1_next_turn else game.player2
