# -*- coding: utf-8 -*-

"""X01 new score calculation functions."""

import math

from lidarts.game.consts import LEG, OPPONENT_LEGS, OPPONENT_SETS, PLAYER_LEGS, PLAYER_SETS, SET
from lidarts.socket.game.X01.new_score.getters import get_best_of, get_draw_possible


def calc_is_drawn(player_dict, is_set):
    """Calculate if match or set is drawn.

    Args:
        player_dict (dict): Dictionary containing game information
        is_set (bool): Indicates whether to calculate set or leg

    Returns:
        bool: True if match/set is drawn, False otherwise
    """
    set_or_match = SET if is_set else LEG
    player_score = PLAYER_SETS if is_set else PLAYER_LEGS
    opponent_score = OPPONENT_SETS if is_set else OPPONENT_LEGS
    best_of = get_best_of(player_dict)
    final_score_drawn = player_dict[player_score] == player_dict[opponent_score] == (best_of[set_or_match] / 2)

    return get_draw_possible(best_of)[set_or_match] and final_score_drawn


def calc_wins_needed(best_of, draw_possible):
    """Calculate needed legs to win sets or sets to win match.

    Args:
        best_of (int): Best of legs/sets constant
        draw_possible (bool): Indicates whether set or match can be drawn

    Returns:
        int: Number of legs/sets needed to win the set/match.
    """
    if draw_possible:
        return (best_of / 2) + 1
    return math.ceil(best_of / 2)


def calc_draw_possible(best_of):
    """Calculate if set/match can be drawn by best of settings.

    Args:
        best_of (int): Best of legs/sets constant

    Returns:
        bool: True if set/match can be drawn, False otherwise
    """
    return (best_of % 2) == 0
