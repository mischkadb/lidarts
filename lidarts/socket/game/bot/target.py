# -*- coding: utf-8 -*-

"""Determine target field for next computer player throw."""

from lidarts.socket.game.bot.computer import cleared_double_in
from lidarts.socket.game.bot.consts import checkout_table

SINGLE_CHECKOUT_THRESH = 20
SINGLE_OUT_T20_THRESH = 60
SINGLE_BULL = 25
DOUBLE_BULL = 50
DOUBLE_CHECKOUT_THRESH = 40
DOUBLE_CHECKOUT_THRESH_THREE_DARTS = 170


def single_out_checkout(remaining_score):  # noqa: WPS212
    """Determine target segment for single out mode.

    Args:
        remaining_score: CPU's remaining score in current leg

    Returns:
        The segment to be targeted next
    """
    if remaining_score > SINGLE_OUT_T20_THRESH:
        return 'T20'
    # always try to checkout on singles if possible
    if remaining_score <= SINGLE_CHECKOUT_THRESH or remaining_score == SINGLE_BULL:
        return f'S{remaining_score}'

    # try to checkout on doubles if possible
    if remaining_score % 2 == 0:
        return f'D{remaining_score // 2}'

    # try to checkout on trebles if possible
    if remaining_score % 3 == 0:
        return f'T{remaining_score // 3}'

    # set up 40 if score between 41 and 59
    if remaining_score > DOUBLE_CHECKOUT_THRESH:
        return f'S{remaining_score - DOUBLE_CHECKOUT_THRESH}'

    # set up 20 if score between 21 and 39
    return f'S{remaining_score - SINGLE_CHECKOUT_THRESH}'


def double_out_checkout(remaining_score):
    """Determine target segment for double and master out mode.

    Args:
        remaining_score: CPU's remaining score in current leg

    Returns:
        The segment to be targeted next
    """
    # computer currently always try to checkout 50 instead of going 18-D16 if appropiate
    if remaining_score == DOUBLE_BULL:
        return 'D25'
    if remaining_score <= DOUBLE_CHECKOUT_THRESH:
        if remaining_score % 2 == 0:
            return f'D{remaining_score // 2}'
        # computer currently always sets up the next highest double (not ideal)
        return 'S1'
    return checkout_table[str(remaining_score)]


def get_target(game):
    """Determine target segment for next CPU player throw.

    Args:
        game: The current X01 game state

    Returns:
        The segment to be targeted next
    """
    if not cleared_double_in(game):
        return 'D20'

    remaining_score = game.p2_score
    out_mode = game.out_mode

    # valid for the naive checkout table
    if remaining_score > DOUBLE_CHECKOUT_THRESH_THREE_DARTS:
        return 'T20'

    # master's out currently does not try to check on trebles
    if out_mode in {'do', 'mo'}:
        return double_out_checkout(remaining_score)
    # Single Out - just naive checkout attempts
    return single_out_checkout(remaining_score)
