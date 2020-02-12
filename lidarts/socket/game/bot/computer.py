# -*- coding: utf-8 -*-

"""A computer opponent for X01 games."""

from lidarts.models import Game
from lidarts.socket.game.bot.consts import levels
from lidarts.socket.game.bot.target import get_target
from lidarts.socket.game.bot.throw import throw_dart


def cleared_double_in(game):
    """Check player double in status in current leg.

    Args:
        game: X01 game state

    Returns:
        True if player cleared double in and may score in current leg
    """
    return not (game.in_mode == 'di' and game.p2_score == game.type)


def is_double_attempt(target, remaining_score):
    """Check if current attempt is an outshot at a double segment.

    Args:
        target: Targeted segment
        remaining_score: Remaining score in current leg

    Returns:
        Boolean state of current attempt as an outshot at a double segment
    """
    double_attempt_threshold = 50
    return target[0] == 'D' and remaining_score <= double_attempt_threshold


def throw_three_darts(game, bot_level):  # noqa: WPS210
    """Simulate an entire three-dart attempt of a CPU player.

    Args:
        game: State of the X01 game
        bot_level: CPU playing strength level

    Returns:
        Total thrown score, missed darts at double and number of leg winning darts
    """
    thrown_scores = []
    double_missed = 0
    remaining_score = game.p2_score - sum(thrown_scores)

    for dart in range(1, 4):
        # acquire target depending on remaining score
        target = get_target(game)

        if is_double_attempt(target, remaining_score):
            double_missed += 1

        # simulate dart throw
        thrown_score, field_hit = throw_dart(target, bot_level)

        if not cleared_double_in and field_hit[0] != 'D':
            thrown_score = 0

        thrown_scores.append(thrown_score)
        remaining_score = game.p2_score - sum(thrown_scores)
        # don't keep throwing if leg won or busted
        if remaining_score == 0:
            double_missed -= 1
            return sum(thrown_scores), double_missed, dart
        elif remaining_score < 0:
            break

    return sum(thrown_scores), double_missed, 0


def get_computer_score(hashid):
    """Pipeline to determine computer player score.

    Args:
        hashid: Unique hashed ID representing the game in the database

    Returns:
        Total thrown score, missed darts at double and number of leg winning darts
    """
    game = Game.query.filter_by(hashid=hashid).first_or_404()

    bot_level = levels[(int(game.opponent_type[-1])) - 1]

    if game.closest_to_bull:
        thrown_score, _ = throw_dart('D25', bot_level)
        return thrown_score

    return throw_three_darts(game, bot_level)
