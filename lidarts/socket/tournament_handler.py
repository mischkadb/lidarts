from flask_login import current_user
from lidarts import socketio, db
from lidarts.models import Tournament, User
from lidarts.socket.utils import broadcast_online_players


@socketio.on('join_tournament', namespace='/chat')
def join_tournament(message):
    hashid = message['hashid']
    tournament = Tournament.query.filter_by(hashid=hashid).first()
    if not tournament or tournament in current_user.tournaments or not tournament.registration_open or tournament.registration_apply:
        return
    current_user.tournaments.append(tournament)
    db.session.commit()
    broadcast_online_players(room=hashid)


@socketio.on('leave_tournament', namespace='/chat')
def leave_tournament(message):
    hashid = message['hashid']
    tournament = Tournament.query.filter_by(hashid=hashid).first()
    if not tournament or tournament not in current_user.tournaments:
        return
    current_user.tournaments.remove(tournament)
    db.session.commit()
    broadcast_online_players(room=hashid)


@socketio.on('apply_for_tournament', namespace='/chat')
def apply_for_tournament(message):
    hashid = message['hashid']
    tournament = Tournament.query.filter_by(hashid=hashid).first()
    if (
        not tournament
        or tournament in current_user.tournaments
        or tournament in current_user.tournaments_banned
        or tournament in current_user.tournaments_applications
        or not tournament.registration_open
        or not tournament.registration_apply
    ):
        return
    current_user.tournaments_applications.append(tournament)
    db.session.commit()


@socketio.on('cancel_tournament_application', namespace='/chat')
def cancel_tournament_application(message):
    hashid = message['hashid']
    tournament = Tournament.query.filter_by(hashid=hashid).first()
    if not tournament or tournament in current_user.tournaments or tournament not in current_user.tournaments_applications:
        return
    current_user.tournaments_applications.remove(tournament)
    db.session.commit()


@socketio.on('confirm_player_application', namespace='/chat')
def confirm_player_application(message):
    hashid = message['hashid']
    tournament = Tournament.query.filter_by(hashid=hashid).first()
    if not tournament or tournament in current_user.tournaments or tournament not in current_user.tournaments_applications:
        return
    current_user.tournaments_applications.remove(tournament)
    current_user.tournaments.append(tournament)
    db.session.commit()


@socketio.on('decline_player_application', namespace='/chat')
def decline_player_application(message):
    hashid = message['hashid']
    tournament = Tournament.query.filter_by(hashid=hashid).first()
    if not tournament or tournament in current_user.tournaments or tournament not in current_user.tournaments_applications:
        return
    current_user.tournaments_applications.remove(tournament)
    db.session.commit()


@socketio.on('kick_player', namespace='/chat')
def kick_player(message):
    hashid = message['hashid']
    user_id = message['user_id']
    tournament = Tournament.query.filter_by(hashid=hashid).first()
    user = User.query.filter_by(id=user_id).first()
    if not tournament or not user or tournament not in user.tournaments:
        return
    user.tournaments.remove(tournament)
    db.session.commit()
    broadcast_online_players(room=hashid)


@socketio.on('ban_player', namespace='/chat')
def ban_player(message):
    hashid = message['hashid']
    user_id = message['user_id']
    tournament = Tournament.query.filter_by(hashid=hashid).first()
    user = User.query.filter_by(id=user_id).first()
    if not tournament or not user or tournament not in user.tournaments:
        return
    user.tournaments.remove(tournament)
    tournament.banned_players.append(user)
    db.session.commit()
    broadcast_online_players(room=hashid)


@socketio.on('unban_player', namespace='/chat')
def ban_player(message):
    hashid = message['hashid']
    user_id = message['user_id']
    tournament = Tournament.query.filter_by(hashid=hashid).first()
    user = User.query.filter_by(id=user_id).first()
    if not tournament or not user or user not in tournament.banned_players:
        return
    tournament.banned_players.remove(user)
    db.session.commit()
