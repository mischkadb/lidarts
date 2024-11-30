# from flask import request
from lidarts import socketio, db
from flask import current_app
from flask_login import current_user
from flask_socketio import  emit, join_room
from lidarts.socket.utils import authenticated_only, send_notification
from lidarts.models import Notification,  UserSettings


@socketio.on('*')
def catch_all(event, data):
    catch_all = current_app.config['SOCKETIO_LOG_CATCH_ALL'] if 'SOCKETIO_LOG_CATCH_ALL' in current_app.config else False
    if catch_all:
        print(event, data)


@socketio.on('connect', namespace='/base')
@authenticated_only
def connect_client():
    # current_user.ping()
    current_app.redis.sadd('last_seen_bulk_user_ids', current_user.id)

    join_room(current_user.username)
    notifications = Notification.query.filter_by(user=current_user.id).all()
    for notification in notifications:
        send_notification(current_user.username, notification.message, notification.author, notification.type, silent=True)

    emit('status_reply', {'status': current_user.status})


@socketio.on('init', namespace='/base')
@authenticated_only
def init(message):
    user_id = message['user_id']
    settings = (
        UserSettings.query
        .filter_by(user=user_id).first()
    )
    if not settings:
        settings = UserSettings(user=user_id)
        db.session.add(settings)
        db.session.commit()
    notification_sound = settings.notification_sound
    emit(
        'settings',
        {'notification_sound': notification_sound, }
    )


@socketio.on('user_heartbeat', namespace='/base')
@authenticated_only
def heartbeat(message):
    user_id = current_user.id
    # current_user.ping()
    current_app.redis.sadd('last_seen_bulk_user_ids', user_id)


@socketio.on('disconnect', namespace='/base')
@authenticated_only
def disconnect_client():
    #current_user.last_seen = datetime.utcnow()
    #current_user.is_online = False
    #db.session.commit()
    current_app.redis.sadd('last_seen_bulk_user_ids', current_user.id)
