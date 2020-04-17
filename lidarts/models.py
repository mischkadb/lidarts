from flask_security import UserMixin, RoleMixin
from lidarts import db
from datetime import datetime, timedelta
import secrets
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship


# Define models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))

tournament_players_association_table = db.Table(
    'association',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('tournament_id', db.Integer, db.ForeignKey('tournaments.id'), primary_key=True),
)

tournament_banned_players_association_table = db.Table(
    'tournament_banned_players_association',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('tournament_id', db.Integer, db.ForeignKey('tournaments.id'), primary_key=True),
)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    alternative_id = db.Column(db.Integer, index=True, unique=True)
    username = db.Column(db.String(25), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    active = db.Column(db.Boolean)
    avatar = db.Column(db.String(15), default=None)
    avatar_version = db.Column(db.Integer, default=0)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())
    last_seen_ingame = db.Column(db.DateTime, default=datetime.utcnow())
    is_online = db.Column(db.Boolean, default=False)
    active_sessions = db.Column(db.Integer, default=0)
    status = db.Column(db.String(15), default='online')
    caller = db.Column(db.String(20), default='default')
    cpu_delay = db.Column(db.Integer, default=0)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    registration_timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    is_backer = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    backer_until = db.Column(db.DateTime, default=None)
    webcam_settings = relationship("WebcamSettings", uselist=False, back_populates="user_object")

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
    player1 = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    player2 = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
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
    status = db.Column(db.String(20), index=True)
    type = db.Column(db.Integer)
    match_json = db.Column(db.JSON)
    in_mode = db.Column(db.String(15))
    out_mode = db.Column(db.String(15))
    begin = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    opponent_type = db.Column(db.String(10))
    public_challenge = db.Column(db.Boolean)
    score_input_delay = db.Column(db.Integer, default=0)
    webcam = db.Column(db.Boolean, default=False)
    jitsi_hashid = db.Column(db.String(10), unique=True)
    tournament = db.Column(db.String(10), db.ForeignKey('tournaments.hashid'), default=None)

    def set_hashid(self):
        self.hashid = secrets.token_urlsafe(8)[:8]

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Chatmessage(db.Model):
    __tablename__ = 'chatmessages'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, index=True)
    tournament_hashid = db.Column(db.String(10), db.ForeignKey('tournaments.hashid'), default=None)


class ChatmessageIngame(db.Model):
    __tablename__ = 'chatmessages_ingame'
    id = db.Column(db.Integer, primary_key=True)
    game_hashid = db.Column(db.String(10), index=True)
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
    user = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
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


class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    user = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    match_alerts = db.Column(db.Boolean, default=True)
    allow_challenges = db.Column(db.Boolean, default=True)
    allow_private_messages = db.Column(db.Boolean, default=True)
    allow_friend_requests = db.Column(db.Boolean, default=True)
    notification_sound = db.Column(db.Boolean, default=True)
    country = db.Column(db.String, default=None)
    last_country_change = db.Column(db.DateTime, default=None)
    checkout_suggestions = db.Column(db.Boolean, default=False)
    show_average_in_chat_list = db.Column(db.Boolean, default=False)
    profile_text = db.Column(db.String(2000), default=None)
    channel_id = db.Column(db.String(30), default=None)
    caller = db.Column(db.String(30), db.ForeignKey('callers.name'), default='default')


class X01Presetting(db.Model):
    __tablename__ = 'x01_presettings'
    user = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    bo_sets = db.Column(db.Integer)
    bo_legs = db.Column(db.Integer)
    two_clear_legs = db.Column(db.Boolean)
    starter = db.Column(db.String(25))
    type = db.Column(db.Integer)
    in_mode = db.Column(db.String(15))
    out_mode = db.Column(db.String(15))
    opponent_type = db.Column(db.String(10))
    level = db.Column(db.Integer)
    public_challenge = db.Column(db.Boolean)
    webcam = db.Column(db.Boolean)
    score_input_delay = db.Column(db.Integer)


class UserStatistic(db.Model):
    __tablename__ = 'user_statistic'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, index=True)
    average = db.Column(db.Float, default=0)
    first9 = db.Column(db.Float, default=0)
    doubles = db.Column(db.Float, default=0)
    total_games = db.Column(db.Integer, default=0)
    darts_thrown = db.Column(db.Integer, default=0)
    matches_u30 = db.Column(db.Integer, default=0)
    matches30_40 = db.Column(db.Integer, default=0)
    matches40_50 = db.Column(db.Integer, default=0)
    matches50_60 = db.Column(db.Integer, default=0)
    matches60_70 = db.Column(db.Integer, default=0)
    matches70_80 = db.Column(db.Integer, default=0)
    matches80_90 = db.Column(db.Integer, default=0)
    matches_o90 = db.Column(db.Integer, default=0)
    wins_u30 = db.Column(db.Integer, default=0)
    wins30_40 = db.Column(db.Integer, default=0)
    wins40_50 = db.Column(db.Integer, default=0)
    wins50_60 = db.Column(db.Integer, default=0)
    wins60_70 = db.Column(db.Integer, default=0)
    wins70_80 = db.Column(db.Integer, default=0)
    wins80_90 = db.Column(db.Integer, default=0)
    wins_o90 = db.Column(db.Integer, default=0)


class SocketConnections(db.Model):
    __tablename__ = 'socket_connections'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    last_reset = db.Column(db.DateTime)


class UsernameChange(db.Model):
    __tablename__ = 'username_changes'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer)
    old_name = db.Column(db.String(25))
    new_name = db.Column(db.String(25))
    timestamp = db.Column(db.DateTime)


class Tournament(db.Model):
    __tablename__ = 'tournaments'
    id = db.Column(db.Integer, primary_key=True)
    creator = db.Column(db.Integer, db.ForeignKey('users.id'))
    hashid = db.Column(db.String(10), unique=True)
    name = db.Column(db.String(50), nullable=False)
    public = db.Column(db.Boolean, default=False)
    registration_open = db.Column(db.Boolean, default=True)
    description = db.Column(db.String(1000))
    external_url = db.Column(db.String(120))
    start_timestamp = db.Column(db.DateTime)
    creation_timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    players = db.relationship(
        'User',
        secondary=tournament_players_association_table,
        lazy=True,
        backref=db.backref('tournaments', lazy=True),
    )
    banned_players = db.relationship(
        'User',
        secondary=tournament_banned_players_association_table,
        lazy=True,
        backref=db.backref('tournaments_banned', lazy=True),
    )

    def __init__(self, **kwargs):
        super(Tournament, self).__init__(**kwargs)
        self.hashid = secrets.token_urlsafe(8)[:8]


class WebcamSettings(db.Model):
    __tablename__ = 'webcam_settings'
    user = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    user_object = relationship("User", back_populates="webcam_settings")
    activated = db.Column(db.Boolean, default=False)
    stream_consent = db.Column(db.Boolean, default=False)
    mobile_app = db.Column(db.Boolean, default=False)
    mobile_follower_mode = db.Column(db.Boolean, default=False)
    force_scoreboard_page = db.Column(db.Boolean, default=False)
    latest_jitsi_hashid = db.Column(db.String(10), default=None)


class Caller(db.Model):
    __tablename__ = 'callers'
    name = db.Column(db.String(30), primary_key=True)
    display_name = db.Column(db.String(50), default=None)
