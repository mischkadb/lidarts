# -*- coding: utf-8 -*-

"""X01 new score leg win checker."""

from lidarts.game.consts import GAME_TYPE, LEG, OPPONENT_LEGS, PLAYER_LEGS, PLAYER_SCORE, SET, TWO_CLEAR_LEGS
from lidarts.socket.game.X01.new_score.calcs import calc_is_drawn
from lidarts.socket.game.X01.new_score.consts import NEW_LEG_DICT
from lidarts.socket.game.X01.new_score.getters import get_wins_needed
from lidarts.socket.game.X01.new_score.set_win_check import check_set_draw, is_set_over_tcl, process_set_win


def _increase_leg_count(player_dict):
    player_legs = player_dict[PLAYER_LEGS]
    wins_needed = get_wins_needed(player_dict=player_dict)

    # leg count increase with check for set win
    if player_dict[TWO_CLEAR_LEGS]:
        player_legs += 1
        set_over = is_set_over_tcl(player_legs, player_dict[OPPONENT_LEGS], wins_needed[LEG])
    else:
        player_legs = (player_legs + 1) % wins_needed[LEG]
        set_over = False

    player_dict[PLAYER_LEGS] = player_legs
    return player_dict, set_over


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
    player_dict, set_over = _increase_leg_count(player_dict)

    # reset score to default value
    player_dict[PLAYER_SCORE] = player_dict[GAME_TYPE]

    if player_dict[PLAYER_LEGS] == 0 or set_over:
        player_dict, current_values, match_json = process_set_win(player_dict, current_values, match_json)

    else:  # no new set unless drawn
        # check for drawn set
        if calc_is_drawn(player_dict, is_set=False):
            player_dict, current_values, match_json = (
                check_set_draw(player_dict, current_values, match_json)
            )

        else:  # no draw, just new leg
            current_values[LEG] = str(int(current_values[LEG]) + 1)
            match_json[current_values[SET]][current_values[LEG]] = NEW_LEG_DICT.copy()

    return player_dict, match_json, current_values
