# -*- coding: utf-8 -*-

"""X01 game utilities."""

import math


def player1_started_leg(leg):
    """Leg starter identifier.

    Args:
        leg: X01 leg with scores for two players

    Returns:
        True if player1 started leg, otherwise False
    """
    # player 1 started leg if player 1 threw more darts (no break) ...
    p1_last_leg_darts = len(leg['1']['scores'])
    p2_last_leg_darts = len(leg['2']['scores'])
    # or player 1 lost the leg and threw the same amount of darts (break)
    p1_leg_score = sum(leg['1']['scores'])
    p2_leg_score = sum(leg['2']['scores'])

    return (
        p1_last_leg_darts > p2_last_leg_darts
        or (
            p1_last_leg_darts == p2_last_leg_darts
            and p1_leg_score < p2_leg_score
        )
    )


def process_leg_win(player_dict, match_json, current_values):
    """Handle end of a X01 leg.

    Checks for set/match wins, handles score resets etc.

    Args:
        player_dict: Stores scores and other player information
        match_json: Current match encoded in set/leg json tree
        current_values: Stores current set, leg and player to throw

    Returns:
        All input values after processing
    """
    # check if draws are possible
    set_draw_possible = (player_dict['bo_sets'] % 2) == 0
    leg_draw_possible = (player_dict['bo_legs'] % 2) == 0

    # amount of legs/sets needed to win
    legs_for_set = (player_dict['bo_legs'] / 2) + 1 if leg_draw_possible else math.ceil(player_dict['bo_legs'] / 2)
    sets_for_match = (player_dict['bo_sets'] / 2) + 1 if set_draw_possible else math.ceil(player_dict['bo_sets'] / 2)

    # leg count increase with check for set win
    if player_dict['two_clear_legs']:
        player_dict['p_legs'] += 1
    else:
        player_dict['p_legs'] = (player_dict['p_legs'] + 1) % legs_for_set
    # reset score to default value
    player_dict['p_score'] = player_dict['type']

    # check if player won set
    if player_dict['p_legs'] == 0 or \
            (player_dict['two_clear_legs'] and
             player_dict['p_legs'] >= legs_for_set and
             player_dict['p_legs'] >= player_dict['o_legs'] + 2):
        player_dict['p_sets'] += 1

        # check if player won match or match drawn
        if player_dict['p_sets'] == sets_for_match or \
                (set_draw_possible and (player_dict['p_sets'] == player_dict['o_sets'] == (player_dict['bo_sets'] / 2))):
            # leg score is needed if best of 1 set
            if player_dict['bo_sets'] == 1 and not player_dict['two_clear_legs']:
                player_dict['p_legs'] = math.ceil((player_dict['bo_legs'] + 0.5) / 2)
            player_dict['status'] = 'completed'
            player_dict['p_score'] = 0  # end score 0 looks nicer
        else:  # match not over, new set
            player_dict['o_legs'] = 0
            current_values['set'] = str(int(current_values['set']) + 1)
            current_values['leg'] = '1'
            match_json[current_values['set']] = {current_values['leg']: {'1': {'scores': [], 'double_missed': []},
                                                                         '2': {'scores': [], 'double_missed': []}}}

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
                match_json[current_values['set']] = {current_values['leg']: {'1': {'scores': [], 'double_missed': []},
                                                                             '2': {'scores': [], 'double_missed': []}}}
        else:  # no draw, just new leg
            current_values['leg'] = str(int(current_values['leg']) + 1)
            match_json[current_values['set']][current_values['leg']] = {'1': {'scores': [], 'double_missed': []},
                                                                        '2': {'scores': [], 'double_missed': []}}

    return player_dict, match_json, current_values


def process_score(hashid, score_value, double_missed, to_finish):
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

    if to_finish:
        match_json[current_values['set']][current_values['leg']][current_values['player']]['to_finish'] = to_finish
    # bug fix - sometimes to_finish is not sent, default to 3
    elif player_dict['p_score'] - score_value == 0:
        match_json[current_values['set']][current_values['leg']][current_values['player']]['to_finish'] = 3

    match_json[current_values['set']][current_values['leg']][current_values['player']]['double_missed'].append(double_missed)

    # check if leg was won
    if player_dict['p_score'] - score_value == 0:
        # add thrown score to match json object
        match_json[current_values['set']][current_values['leg']][current_values['player']]['scores'].append(score_value)

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
            game.p1_score = game.type
            game.p2_score = game.type
    # check if busted
    elif player_dict['p_score'] - score_value < 0:
        match_json[current_values['set']][current_values['leg']][current_values['player']]['scores'].append(0)
    # Double/Master out: score cannot drop to 1
    elif game.out_mode in ['do', 'mo'] and player_dict['p_score'] - score_value == 1:
        match_json[current_values['set']][current_values['leg']][current_values['player']]['scores'].append(0)
    # nothing special happened, just score
    else:
        player_dict['p_score'] -= score_value
        match_json[current_values['set']][current_values['leg']][current_values['player']]['scores'].append(score_value)

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
    # no new leg, other player's turn
    else:
        game.p1_next_turn = not game.p1_next_turn
    db.session.commit()
    return game


def current_turn_user_id(hashid):
    game = Game.query.filter_by(hashid=hashid).first_or_404()
    return game.player1 if game.p1_next_turn else game.player2


