# -*- coding: utf-8 -*-

"""X01 new score processing utility getters."""

from lidarts.game.consts import BEST_OF_LEGS, BEST_OF_SETS, LEG, SET
from lidarts.socket.game.X01.new_score.calcs import calc_draw_possible, calc_wins_needed


def get_best_of(player_dict):
    """Get dictionary with best of leg/set values given the player_dict.

    Args:
        player_dict (dict): Dictionary containing game information

    Returns:
        dict: Dictionary with best of leg/set integers
    """
    return {
        LEG: player_dict[BEST_OF_LEGS],
        SET: player_dict[BEST_OF_SETS],
    }


def get_draw_possible(best_of=None, player_dict=None):
    """Get dictionary with draw possible values given best of set/leg dict.

    Args:
        best_of (dict): Dictionary with best of leg/set integers
        player_dict (dict): Dictionary containing game information

    Returns:
        dict: Dictionary with draw possible bools
    """
    if player_dict:
        best_of = get_best_of(player_dict)

    return {
        LEG: calc_draw_possible(best_of[LEG]),
        SET: calc_draw_possible(best_of[SET]),
    }


def get_wins_needed(best_of=None, draw_possible=None, player_dict=None):
    """Get dictionary with amount of legs/sets needed to win set/match.

    Args:
        best_of (dict): Dictionary with best of leg/set integers
        draw_possible(dict): Dictionary with draw possible bools
        player_dict (dict): Dictionary containing game information

    Returns:
        dict: Dictionary with leg/set ints needed to win set/match
    """
    if player_dict:
        best_of = get_best_of(player_dict)
        draw_possible = get_draw_possible(best_of)

    return {
        LEG: calc_wins_needed(best_of[LEG], draw_possible[LEG]),
        SET: calc_wins_needed(best_of[SET], draw_possible[SET]),
    }
