from flask import session, request
from flask_socketio import emit
from lidarts import socketio, db
from lidarts.models import Game


@socketio.on('send_score', namespace='/game')
def send_score(message):
    if not message['score']:
        return
    score_value = int(message['score'])
    game = Game.query.filter_by(hashid=message['hashid']).first_or_404()
    if game.p1_next_turn:
        game.p1_score -= score_value
    else:
        game.p2_score -= score_value
    game.p1_next_turn = not game.p1_next_turn
    db.session.commit()
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('score_response',
         {'score1': game.p1_score, 'score2': game.p2_score})


@socketio.on('connect', namespace='/game')
def connect():
    print('Client connected', request.sid)


@socketio.on('init', namespace='/game')
def init(message):
    game = Game.query.filter_by(hashid=message['hashid']).first_or_404()
    score1 = game.p1_score
    score2 = game.p2_score
    emit('score_response',
         {'score1': score1, 'score2': score2})


@socketio.on('disconnect', namespace='/game')
def disconnect():
    print('Client disconnected', request.sid)
