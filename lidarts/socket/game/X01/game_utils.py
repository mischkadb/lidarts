# -*- coding: utf-8 -*-

"""X01 game utilities."""

from lidarts.game.consts import PLAYER_ONE, PLAYER_TWO, SCORES
from lidarts.models import Game


def player1_started_leg(leg):
    """Leg starter identifier.

    Args:
        leg: X01 leg with scores for two players

    Returns:
        True if player1 started leg, otherwise False
    """
    # player 1 started leg if player 1 threw more darts (no break) ...
    p1_last_leg_darts = len(leg[PLAYER_ONE][SCORES])
    p2_last_leg_darts = len(leg[PLAYER_TWO][SCORES])
    # or player 1 lost the leg and threw the same amount of darts (break)
    p1_leg_score = sum(leg[PLAYER_ONE][SCORES])
    p2_leg_score = sum(leg[PLAYER_TWO][SCORES])

    return (
        p1_last_leg_darts > p2_last_leg_darts
        or (
            p1_last_leg_darts == p2_last_leg_darts
            and p1_leg_score < p2_leg_score
        )
    )


def current_turn_user_id(hashid):
    """Identify user ID of player to throw next.

    Args:
        hashid: Hashed ID of the game

    Returns:
        ID of the player to throw next
    """
    game = Game.query.filter_by(hashid=hashid).first_or_404()
    return game.player1 if game.p1_next_turn else game.player2
