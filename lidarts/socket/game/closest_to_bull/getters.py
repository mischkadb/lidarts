# -*- coding: utf-8 -*-

"""Closest to bull utility getters."""

from flask_login import current_user

player1 = '1'
player2 = '2'


def get_players(game, p1_attempts, p2_attempts, computer):
    """Identify next player to throw at bull.

    Args:
        game: X01 game encoded in dictionary
        p1_attempts: Player 1 results at bull
        p2_attempts: Player 2 results at bull
        computer: Flag for a game vs. the AI

    Returns:
        Player next to throw and the opposing player
    """
    # local game, player 1 throws all three darts first
    if game.player1 == game.player2:
        p1_attempts_count = len(p1_attempts)
        p2_attempts_count = len(p2_attempts)
        if p1_attempts_count % 3 == 0 and p1_attempts_count > p2_attempts_count:
            player = 2
        else:
            player = 1
    # computer game
    elif computer:
        player = player2
    # online game
    else:
        player = player1 if game.player1 == current_user.id else player2
    other_player = player1 if player == player2 else player2

    return player, other_player


def get_player_score(attempts, attempts_other_player):
    """Get a player's scores from the current round.

    Args:
        attempts: Current player closest to bull scores
        attempts_other_player: Other player closest to bull scores

    Returns:
        The player's current round scores
    """
    attempts_count = len(attempts)
    # emit throw score to players
    if attempts_count % 3 == 1:
        return attempts[-1:]
    elif attempts_count % 3 == 2:
        return attempts[-2:]
    elif attempts_count % 3 == 0 and attempts_count > len(attempts_other_player):
        return attempts[-3:]
    return []
