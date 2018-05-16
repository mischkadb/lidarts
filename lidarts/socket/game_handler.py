from flask import session, request
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect
from lidarts import socketio

score1 = 501
score2 = 501
p1_turn = True


@socketio.on('send_score', namespace='/game')
def send_score(message):
    global score1, score2, p1_turn
    if p1_turn:
        score1 -= int(message['score'])
    else:
        score2 -= int(message['score'])
    p1_turn = not p1_turn
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('score_response',
         {'score1': str(score1), 'score2': str(score2)})


@socketio.on('connect', namespace='/game')
def test_connect():
    emit('my_response', {'data': 'Connected', 'count': 0})
    print('Client connected', request.sid)


@socketio.on('disconnect', namespace='/game')
def test_disconnect():
    print('Client disconnected', request.sid)
