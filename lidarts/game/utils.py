from lidarts import db
from lidarts.models import User


def get_name_by_id(id):
    if id is None:
        return 'Guest'
    user = User.query.get(id)
    if user:
        return user.username
    else:
        return None
