# -*- coding: utf-8 -*-

"""Closest to bull processing.

Playoff between players to find out the starting player.
Both players throw 3 darts at bull. Only S25 and D25 count.
First better throw starts the match. Repeat if drawn.
"""

import json

from lidarts import db
from lidarts.socket.game.closest_to_bull.emits import emit_closest_to_bull_result, emit_new_score
from lidarts.socket.game.closest_to_bull.getters import get_players


def has_to_wait(attempts, next_player, other_player):
    """Evaluate if player has to wait for other player's throw.

    Args:
        attempts: X01 game encoded in dictionary
        next_player: The next player expected to throw
        other_player: The player waiting for next_player to throw

    Returns:
        True if player has to wait. False otherwise.
    """
    next_player_attempts_count = len(attempts[next_player])
    other_player_attempts_count = len(attempts[other_player])
    return next_player_attempts_count % 3 == 0 and next_player_attempts_count > other_player_attempts_count


def process_closest_to_bull(game, score_value, computer=False):
    """Handle new closest to bull score entries.

    Args:
        game: X01 game encoded in dictionary
        score_value: New score to process
        computer: Flag for a game vs. the AI
    """
    # Refuse nonsense score
    if score_value > 60:
        return

    closest_to_bull_json = json.loads(game.closest_to_bull_json)
    attempts = {
        1: closest_to_bull_json[0],
        2: closest_to_bull_json[1],
    }

    next_player, other_player = get_players(game, attempts, computer)

    # check if player has to wait for other player

    if has_to_wait(attempts, next_player, other_player):
        return

    # append score
    bull_scores = (25, 50)
    if score_value in bull_scores:
        attempts[next_player].append(score_value)
    else:
        attempts[next_player].append(0)
    game.closest_to_bull_json = json.dumps(closest_to_bull_json)
    db.session.commit()

    emit_closest_to_bull_result(game, attempts)

    emit_new_score(game, attempts)
