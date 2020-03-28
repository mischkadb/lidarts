from flask import current_app, request
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from lidarts import socketio, db
from lidarts.models import Game, User, UserStatistic


def broadcast_public_challenges():
    public_challenges = []
    public_challenges_query = (
        Game.query
        .filter_by(public_challenge=True)
        .filter_by(status='challenged')
        .join(User, User.id == Game.player1).add_columns(User.username)
        .join(UserStatistic, UserStatistic.user == Game.player1).add_columns(UserStatistic.average)
        .order_by(Game.id).all()
    )

    for game, username, average in public_challenges_query:
        public_challenge = {
            'hashid': game.hashid,
            'username': username,
            'type': game.type,
            'bo_sets': game.bo_sets,
            'bo_legs': game.bo_legs,
            'in_mode': game.in_mode,
            'out_mode': game.out_mode,
            'two_clear_legs': game.two_clear_legs,
            'closest_to_bull': game.closest_to_bull,
            'average': average,
        }
        public_challenges.append(public_challenge)

    emit(
        'broadcast_public_challenges',
        {'public_challenges': public_challenges},
        namespace='/public_challenge',
        broadcast=True,
        )


@socketio.on('connect', namespace='/public_challenge')
def connect():
    broadcast_public_challenges()


@socketio.on('disconnect', namespace='/public_challenge')
def disconnect():
    # print('Client disconnected', request.sid)
    pass

