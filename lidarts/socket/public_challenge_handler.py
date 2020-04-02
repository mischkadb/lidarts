from flask import current_app, request
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from lidarts import socketio, db
from lidarts.models import Game, User, UserStatistic
from datetime import datetime, timedelta


def broadcast_public_challenges():
    public_challenges = []
    public_challenges_query = (
        Game.query
        .filter_by(status='challenged')
        .filter_by(public_challenge=True)
        .join(User, User.id == Game.player1).add_columns(User.username, User.last_seen)
        .join(UserStatistic, UserStatistic.user == Game.player1).add_columns(UserStatistic.average)
        .order_by(Game.id).all()
    )

    for game, username, last_seen, average in public_challenges_query:
        if last_seen < datetime.utcnow() - timedelta(minutes=1):
            game.status = 'aborted'
            continue

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

    db.session.commit()
    emit(
        'broadcast_public_challenges',
        {'public_challenges': public_challenges},
        namespace='/public_challenge',
        broadcast=True,
        )


@socketio.on('connect', namespace='/public_challenge')
def connect_public_challenge():
    broadcast_public_challenges()


@socketio.on('disconnect', namespace='/public_challenge_waiting')
def disconnect():
    public_challenges_query = (
        Game.query
        .filter_by(player1=current_user.id)
        .filter_by(public_challenge=True)
        .filter_by(status='challenged')
        .all()
    )
    for game in public_challenges_query:
        game.status = 'aborted'
    db.session.commit()
    broadcast_public_challenges()
