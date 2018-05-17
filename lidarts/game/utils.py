from lidarts import db
from lidarts.models import User


def get_name_by_id(id):
    if id == 0:
        return 'Guest'
    user = User.query.get(id)
    if user:
        return user.username
    else:
        return None
