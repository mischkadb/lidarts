from flask_login import current_user
from lidarts import socketio, db
from lidarts.game.utils import get_name_by_id
from lidarts.models import Tournament, User, Notification
from flask_babelex import gettext
from flask_socketio import emit
from lidarts.socket.utils import broadcast_online_players, send_notification


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


@socketio.on('invite_player', namespace='/chat')
def invite_username(message):
    hashid = message['hashid']
    username = message['username']
    tournament = Tournament.query.filter_by(hashid=hashid).first()
    user = User.query.filter_by(username=username).first()
    if not tournament or not user or tournament in user.tournaments or tournament in user.tournaments_invitations:
        return
    user.tournaments_invitations.append(tournament)
    db.session.commit()


@socketio.on('cancel_invitation', namespace='/chat')
def cancel_invitation(message):
    hashid = message['hashid']
    username = message['username']
    tournament = Tournament.query.filter_by(hashid=hashid).first()
    user = User.query.filter_by(username=username).first()
    if not tournament or not user or tournament in user.tournaments or not tournament in user.tournaments_invitations:
        return
    user.tournaments_invitations.remove(tournament)
    db.session.commit()


@socketio.on('accept_tournament_invitation', namespace='/chat')
def accept_tournament_invitation(message):
    hashid = message['hashid']
    tournament = Tournament.query.filter_by(hashid=hashid).first()
    if not tournament or tournament in current_user.tournaments or not tournament in current_user.tournaments_invitations:
        return
    current_user.tournaments_invitations.remove(tournament)
    current_user.tournaments.append(tournament)
    db.session.commit()


@socketio.on('decline_tournament_invitation', namespace='/chat')
def decline_tournament_invitation(message):
    hashid = message['hashid']
    tournament = Tournament.query.filter_by(hashid=hashid).first()
    if not tournament or tournament in current_user.tournaments or not tournament in current_user.tournaments_invitations:
        return
    current_user.tournaments_invitations.remove(tournament)
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
def unban_player(message):
    hashid = message['hashid']
    user_id = message['user_id']
    tournament = Tournament.query.filter_by(hashid=hashid).first()
    user = User.query.filter_by(id=user_id).first()
    if not tournament or not user or user not in tournament.banned_players:
        return
    tournament.banned_players.remove(user)
    db.session.commit()


@socketio.on('start_next_game_request', namespace='/chat')
def start_next_game_request(message):
    hashid = message['hashid']
    tournament = Tournament.query.filter_by(hashid=hashid).first()
    if not tournament or current_user not in tournament.players:
        return

    for round_ in tournament.stages[0].rounds:
        for tournament_game in round_.games:
            if not tournament_game.game:
                continue

            game = tournament_game.game
            if game.status != 'scheduled':
                continue

            if game.player1 == current_user.id and game.player2 and not tournament_game.p1_ready:
                tournament_game.p1_ready = True
                if tournament_game.p2_ready:
                    game.status = 'started'
                    emit('game_ready', {'hashid': hashid}, room=hashid)
                else:
                    message = gettext('Tournament opponent is ready')
                    notification = Notification(user=game.player2, message=message, author=current_user.username, type='tournament_next_game')
                    db.session.add(notification)
                    p2_name = get_name_by_id(game.player2)
                    send_notification(p2_name, message, current_user.username, 'tournament_next_game')
            elif game.player2 == current_user.id and game.player1 and not tournament_game.p2_ready:
                tournament_game.p2_ready = True
                if tournament_game.p1_ready:
                    game.status = 'started'
                    emit('game_ready', {'hashid': hashid}, room=hashid)
                else:
                    message = gettext('Tournament opponent is ready')
                    notification = Notification(user=game.player1, message=message, author=current_user.username, type='tournament_next_game')
                    db.session.add(notification)
                    p1_name = get_name_by_id(game.player1)
                    send_notification(p1_name, message, current_user.username, 'tournament_next_game')

            db.session.commit()
            return
