# -*- coding: utf-8 -*-

"""X01 game utilities."""

import json
from datetime import datetime

from lidarts import db
from lidarts.game import status_consts as status
from lidarts.game.consts import (
    DARTS_TO_FINISH,
    DOUBLE_MISSED,
    GAME_STATUS,
    LEG,
    PLAYER,
    PLAYER_ONE,
    PLAYER_TWO,
    SCORES,
    SET,
)
from lidarts.models import Game
from lidarts.socket.game.broadcasts import broadcast_game_completed
from lidarts.socket.utils import game_from_dict, player_to_dict


def process_score(hashid, score_value, double_missed, to_finish):
    game = Game.query.filter_by(hashid=hashid).first_or_404()
    match_json = json.loads(game.match_json)

    if game.status != status.STARTED:
        return game

    current_values = {
        SET: str(game.p1_sets + game.p2_sets + 1),
        LEG: str(game.p1_legs + game.p2_legs + 1),
        PLAYER: PLAYER_ONE if game.p1_next_turn is True else PLAYER_TWO,
    }
    player_dict = player_to_dict(game, game.p1_next_turn)
    new_leg_starter = 0  # used for leg starting player

    if to_finish:
        match_json[current_values[SET]][current_values[LEG]][current_values[PLAYER]][DARTS_TO_FINISH] = to_finish
    # bug fix - sometimes to_finish is not sent, default to 3
    elif player_score - score_value == 0:
        match_json[current_values[SET]][current_values[LEG]][current_values[PLAYER]][DARTS_TO_FINISH] = 3

    match_json[current_values[SET]][current_values[LEG]][current_values[PLAYER]][DOUBLE_MISSED].append(double_missed)

    # check if leg was won
    if player_score - score_value == 0:
        # add thrown score to match json object
        match_json[current_values[SET]][current_values[LEG]][current_values[PLAYER]][SCORES].append(score_value)

        # check who begins next leg
        new_leg_starter = PLAYER_TWO \
            if player1_started_leg(match_json[current_values[SET]][current_values[LEG]]) else PLAYER_ONE
        current_set = current_values[SET]

        # check for won sets, won match, update scores etc.
        player_dict, match_json, current_values = _process_leg_win(player_dict, match_json, current_values)

        # set mode only: new sets are started alternately, need to recheck leg starter)
        if current_values[SET] > current_set and len(match_json[current_set]) % 2 == 0:
            new_leg_starter = PLAYER_TWO if new_leg_starter == PLAYER_ONE else PLAYER_ONE

        # reset player scores to default
        if not player_dict[GAME_STATUS] == status.COMPLETED:
            game.p1_score = game.type
            game.p2_score = game.type
    # check if busted
    elif player_score - score_value < 0:
        match_json[current_values[SET]][current_values[LEG]][current_values[PLAYER]][SCORES].append(0)
    # Double/Master out: score cannot drop to 1
    elif game.out_mode in ['do', 'mo'] and player_score - score_value == 1:
        match_json[current_values[SET]][current_values[LEG]][current_values[PLAYER]][SCORES].append(0)
    # nothing special happened, just score
    else:
        player_score -= score_value
        match_json[current_values[SET]][current_values[LEG]][current_values[PLAYER]][SCORES].append(score_value)

    # save everything back into the model object
    game = game_from_dict(game, player_dict)
    game.match_json = json.dumps(match_json)

    if game.status == status.COMPLETED:
        game.end = datetime.utcnow()
        if not game.opponent_type.startswith('computer'):
            broadcast_game_completed(game)
    # new leg
    elif new_leg_starter:
        game.p1_next_turn = new_leg_starter == PLAYER_ONE
    # no new leg, other player's turn
    else:
        game.p1_next_turn = not game.p1_next_turn
    db.session.commit()

    return game
