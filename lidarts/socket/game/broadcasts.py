# -*- coding: utf-8 -*-

"""X01 socket broadcasts."""

from flask_socketio import emit

from lidarts.models import User


def broadcast_game_aborted(game):
    """Emit message in case of game abortion.

    Args:
        game: dictionary with X01 game state
    """
    emit('game_aborted', {'hashid': game.hashid}, room=game.hashid, namespace='/game', broadcast=True)


def get_player_name(player_id):
    """Query username given a player ID.

    Args:
        player_id: Player's ID in database.

    Returns:
        Player's username
    """
    player_name, = (
        User.query.
        with_entities(User.username).
        filter_by(id=player_id).
        first_or_404()
    )

    return player_name


def broadcast_new_game(game):
    """Emit message in case of new game.

    Args:
        game: dictionary with X01 game state
    """
    p1_name = get_player_name(game.player1)
    p2_name = get_player_name(game.player2)

    emit(
        'send_system_message_new_game',
        {'hashid': game.hashid, 'p1_name': p1_name, 'p2_name': p2_name},
        broadcast=True,
        namespace='/chat',
    )


def broadcast_game_completed(game):
    """Emit message in case of finished game.

    Args:
        game: dictionary with X01 game state
    """
    p1_name = get_player_name(game.player1)
    p2_name = get_player_name(game.player2)

    if game.bo_sets > 1:
        p1_score = game.p1_sets
        p2_score = game.p2_sets
    else:
        p1_score = game.p1_legs
        p2_score = game.p2_legs

    emit(
        'send_system_message_game_completed',
        {
            'hashid': game.hashid,
            'p1_name': p1_name,
            'p2_name': p2_name,
            'p1_score': p1_score,
            'p2_score': p2_score,
        },
        broadcast=True,
        namespace='/chat',
    )
