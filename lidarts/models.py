from flask_security import UserMixin, RoleMixin
from lidarts import db
from datetime import datetime, timedelta
import secrets
from sqlalchemy.ext.associationproxy import association_proxy


# Define models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    active = db.Column(db.Boolean)
    avatar = db.Column(db.String(15), default=None)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen_ingame = db.Column(db.DateTime, default=datetime.utcnow)
    is_online = db.Column(db.Boolean, default=False)
    active_sessions = db.Column(db.Integer, default=0)
    status = db.Column(db.String(15), default='online')
    caller = db.Column(db.String(20), default='default')
    cpu_delay = db.Column(db.Integer, default=0)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    requested_friend_reqs = db.relationship(
        'FriendshipRequest',
        foreign_keys='FriendshipRequest.requesting_user_id',
        backref='requesting_user'
    )
    received_friend_reqs = db.relationship(
        'FriendshipRequest',
        foreign_keys='FriendshipRequest.receiving_user_id',
        backref='receiving_user'
    )
    aspiring_friends = association_proxy('received_friend_reqs', 'requesting_user')
    desired_friends = association_proxy('requested_friend_reqs', 'receiving_user')

    requested_friend_confs = db.relationship(
        'Friendship',
        foreign_keys='Friendship.user1_id',
        backref='requesting_friend'
    )
    received_friend_confs = db.relationship(
        'Friendship',
        foreign_keys='Friendship.user2_id',
        backref='receiving_friend'
    )
    friends_requested = association_proxy('received_friend_confs', 'requesting_friend')
    friends_received = association_proxy('requested_friend_confs', 'receiving_friend')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def ping(self):
        self.last_seen = datetime.utcnow()
        last_online = self.is_online
        self.is_online = True
        db.session.commit()
        return last_online != self.is_online

    def recently_online(self):
        return self.is_online or self.last_seen > datetime.utcnow() - timedelta(minutes=1)


class FriendshipRequest(db.Model):
    __tablename__ = 'friendship_requests'
    requesting_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    receiving_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)


class Friendship(db.Model):
    __tablename__ = 'friendships'
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    hashid = db.Column(db.String(10), unique=True)
    player1 = db.Column(db.Integer, db.ForeignKey('users.id'))
    player2 = db.Column(db.Integer, db.ForeignKey('users.id'))
    bo_sets = db.Column(db.Integer, nullable=False)
    bo_legs = db.Column(db.Integer, nullable=False)
    two_clear_legs = db.Column(db.Boolean)
    p1_sets = db.Column(db.Integer)
    p2_sets = db.Column(db.Integer)
    p1_legs = db.Column(db.Integer)
    p2_legs = db.Column(db.Integer)
    p1_score = db.Column(db.Integer)
    p2_score = db.Column(db.Integer)
    p1_next_turn = db.Column(db.Boolean)
    closest_to_bull = db.Column(db.Boolean)
    closest_to_bull_json = db.Column(db.JSON)
    status = db.Column(db.String(20))
    type = db.Column(db.Integer)
    match_json = db.Column(db.JSON)
    in_mode = db.Column(db.String(15))
    out_mode = db.Column(db.String(15))
    begin = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    opponent_type = db.Column(db.String(10))

    def set_hashid(self):
        self.hashid = secrets.token_urlsafe(8)[:8]

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Chatmessage(db.Model):
    __tablename__ = 'chatmessages'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime)


class ChatmessageIngame(db.Model):
    __tablename__ = 'chatmessages_ingame'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_hashid = db.Column(db.String(10), primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime)


class Privatemessage(db.Model):
    __tablename__ = 'privatemessages'
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime)


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.String(500))
    author = db.Column(db.String(30))
    type = db.Column(db.String(30))


class BoardCoordinates(db.Model):
    __tablename__ = 'boardcoordinates'
    id = db.Column(db.Integer(), primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
    x1 = db.Column(db.Integer)
    y1 = db.Column(db.Integer)
    x2 = db.Column(db.Integer)
    y2 = db.Column(db.Integer)
    x3 = db.Column(db.Integer)
    y3 = db.Column(db.Integer)


class UserStatistic(db.Model):
    __tablename__ = 'user_statistic'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
    average = db.Column(db.Float, default=0)
    first9 = db.Column(db.Float, default=0)
    doubles = db.Column(db.Float, default=0)
    total_games = db.Column(db.Integer, default=0)
    darts_thrown = db.Column(db.Integer, default=0)


class SocketConnections(db.Model):
    __tablename__ = 'socket_connections'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    last_reset = db.Column(db.DateTime)
