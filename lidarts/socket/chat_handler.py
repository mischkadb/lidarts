from flask import request
from flask_socketio import emit
from lidarts import socketio, db
from lidarts.models import User, Chatmessage
from datetime import datetime


@socketio.on('connect', namespace='/chat')
def connect():
    print('Client connected', request.sid)


@socketio.on('broadcast_chat_message', namespace='/chat')
def broadcast_chat_message(message):
    print(message)
    new_message = Chatmessage(message=message['message'], author=message['user_id'], timestamp=datetime.now())
    db.session.add(new_message)
    db.session.commit()

    author = User.query.with_entities(User.username) \
        .filter_by(id=new_message.author).first_or_404()[0]

    emit('send_message', {'author': author, 'message': new_message.message,
                          'timestamp': new_message.timestamp.strftime("%H:%M:%S")},
         broadcast=True)


@socketio.on('disconnect', namespace='/chat')
def disconnect():
    print('Client disconnected', request.sid)
