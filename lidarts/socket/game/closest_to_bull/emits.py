# -*- coding: utf-8 -*-

"""Closest to bull utility emitters."""

from flask_socketio import emit

from lidarts import db
from lidarts.socket.game.closest_to_bull.getters import get_player_score


def emit_new_score(game, p1_attempts, p2_attempts):
    """Emit latest closest to bull score result.

    Args:
        game: X01 game encoded in dictionary
        p1_attempts: Player 1 closest to bull scores
        p2_attempts: Player 2 closest to bull scores
    """
    # emit throw score to players
    p1_score = get_player_score(p1_attempts, p2_attempts)
    p2_score = get_player_score(p2_attempts, p1_attempts)

    emit(
        'closest_to_bull_score',
        {
            'hashid': game.hashid,
            'p1_score': p1_score,
            'p2_score': p2_score,
        },
        room=game.hashid,
        broadcast=True,
    )


def emit_closest_to_bull_result(
    game,
    p1_attempts,
    p2_attempts,
    next_player_attempts,
    other_player_attempts_count,
):
    """Emit latest closest to bull score result.

    Args:
        game: X01 game encoded in dictionary
        p1_attempts: Player 1 closest to bull scores
        p2_attempts: Player 2 closest to bull scores
        next_player_attempts: Next player closest to bull scores
        other_player_attempts_count: Other player closest to bull score count
    """
    p1_last_attempt = p1_attempts[-3:]
    p2_last_attempt = p2_attempts[-3:]
    next_player_attempts_count = len(next_player_attempts)

    # check if both players threw 3 darts
    if next_player_attempts_count % 3 == 0 and next_player_attempts_count == other_player_attempts_count:
        # check if done
        for attempt, _ in enumerate(next_player_attempts):
            if p1_attempts[attempt] != p2_attempts[attempt]:
                game.p1_next_turn = p1_attempts[attempt] > p2_attempts[attempt]

                game.closest_to_bull = False
                db.session.commit()
                emit(
                    'closest_to_bull_completed',
                    {
                        'hashid': game.hashid,
                        'p1_won': game.p1_next_turn,
                        'p1_score': p1_last_attempt,
                        'p2_score': p2_last_attempt,
                    },
                    room=game.hashid,
                    broadcast=True,
                )
                return

        # draw, next round
        emit(
            'closest_to_bull_draw',
            {
                'hashid': game.hashid,
                'p1_score': p1_last_attempt,
                'p2_score': p2_last_attempt,
            },
            room=game.hashid,
            broadcast=True,
        )
        return
