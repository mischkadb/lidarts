# -*- coding: utf-8 -*-

"""X01 new score processing utilities."""

import math

from lidarts.game import status_consts as status
from lidarts.game.consts import (
    BEST_OF_SETS,
    GAME_STATUS,
    LEG,
    OPPONENT_LEGS,
    OPPONENT_SETS,
    PLAYER_LEGS,
    PLAYER_ONE,
    PLAYER_SCORE,
    PLAYER_SETS,
    SET,
    TWO_CLEAR_LEGS,
)
from lidarts.socket.game.X01.new_score.calcs import calc_is_drawn
from lidarts.socket.game.X01.new_score.consts import NEW_LEG_DICT
from lidarts.socket.game.X01.new_score.getters import get_best_of, get_wins_needed


def is_set_over_tcl(player_legs, opponent_legs, legs_for_set):
    """Set score check with two clear leg rule.

    Args:
        player_legs: Player leg count in current set
        opponent_legs: Opponent leg count in current set
        legs_for_set: Leg wins needed for set

    Returns:
        True if current set is over, otherwise False
    """
    return player_legs >= legs_for_set and player_legs >= opponent_legs + 2


def _is_match_over(player_dict, sets_needed, draw_possible, best_of_sets):
    player_won = player_dict[PLAYER_SETS] == sets_needed
    match_drawn = calc_is_drawn(player_dict, is_set=True)
    return player_won or match_drawn


def process_set_win(player_dict, current_values, match_json):
    """Handle end of a X01 set.

    Checks for match wins, handles new set dict sanity.

    Args:
        player_dict: Stores scores and other player information
        match_json: Current match encoded in set/leg json tree
        current_values: Stores current set, leg and player to throw

    Returns:
        All input values after processing
    """
    best_of_legs = get_best_of(player_dict)[LEG]
    player_dict[PLAYER_SETS] += 1

    if _is_match_over():
        # leg score is needed if best of 1 set
        if player_dict[BEST_OF_SETS] == 1 and not player_dict[TWO_CLEAR_LEGS]:
            player_dict[PLAYER_LEGS] = math.ceil((best_of_legs + 0.5) / 2)
        player_dict[GAME_STATUS] = status.COMPLETED
        player_dict[PLAYER_SCORE] = 0  # end score 0 looks nicer
    else:  # match not over, new set
        player_dict[OPPONENT_LEGS] = 0
        current_values[SET] = str(int(current_values[SET]) + 1)
        current_values[LEG] = PLAYER_ONE
        match_json[current_values[SET]] = {
            current_values[LEG]: NEW_LEG_DICT.copy(),
        }

    return player_dict, current_values, match_json


def check_set_draw(player_dict, current_values, match_json):
    """Check for a drawn set.

    Args:
        player_dict: Stores scores and other player information
        match_json: Current match encoded in set/leg json tree
        current_values: Stores current set, leg and player to throw

    Returns:
        All input values after processing
    """
    sets_needed_to_win = get_wins_needed(player_dict=player_dict)[SET]

    player_dict[PLAYER_SETS] += 1
    player_dict[OPPONENT_SETS] += 1
    # check if a player won the match
    if player_dict[PLAYER_SETS] == sets_needed_to_win or player_dict[OPPONENT_SETS] == sets_needed_to_win:
        player_dict[GAME_STATUS] = status.COMPLETED
        player_dict[PLAYER_SCORE] = 0
    # check if match is drawn - redundant atm, could be merged with game win
    elif calc_is_drawn(player_dict, is_set=True):
        player_dict[GAME_STATUS] = status.COMPLETED
        player_dict[PLAYER_SCORE] = 0
    # no one won the match, new set
    else:
        player_dict[PLAYER_LEGS] = 0
        player_dict[OPPONENT_LEGS] = 0
        current_values[SET] = str(int(current_values[SET]) + 2)  # + 2 because both players won a set
        current_values[LEG] = PLAYER_ONE
        match_json[current_values[SET]] = {current_values[LEG]: NEW_LEG_DICT.copy()}

    return player_dict, current_values, match_json
