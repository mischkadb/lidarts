from lidarts.models import User
from datetime import datetime, timedelta


def get_user_status(user):
    if user.last_seen_ingame and user.last_seen_ingame > datetime.utcnow() - timedelta(seconds=15):
        return 'ingame'
    elif user.last_seen and user.last_seen > datetime.utcnow() - timedelta(seconds=15):
        return user.status
    else:
        return 'offline'
