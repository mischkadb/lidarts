from flask import session, request, jsonify
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
         {'p1_score': game.p1_score, 'p2_score': game.p2_score, 'p1_sets': game.p1_sets,
          'p2_sets': game.p2_sets, 'p1_legs': game.p1_legs, 'p2_legs': game.p2_legs})


@socketio.on('connect', namespace='/game')
def connect():
    print('Client connected', request.sid)


@socketio.on('init', namespace='/game')
def init(message):
    game = Game.query.filter_by(hashid=message['hashid']).first_or_404()
    emit('score_response', {'p1_score': game.p1_score, 'p2_score': game.p2_score, 'p1_sets': game.p1_sets,
                            'p2_sets': game.p2_sets, 'p1_legs': game.p1_legs, 'p2_legs': game.p2_legs})


@socketio.on('disconnect', namespace='/game')
def disconnect():
    print('Client disconnected', request.sid)
