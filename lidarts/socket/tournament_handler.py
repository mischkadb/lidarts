from flask_login import current_user
from lidarts import socketio, db
from lidarts.models import Tournament
from lidarts.socket.utils import broadcast_online_players


@socketio.on('join_tournament', namespace='/chat')
def join_tournament(message):
    hashid = message['hashid']
    tournament = Tournament.query.filter_by(hashid=hashid).first()
    if not tournament or tournament in current_user.tournaments:
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
