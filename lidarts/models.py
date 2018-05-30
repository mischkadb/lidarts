from flask_security import UserMixin, RoleMixin
from lidarts import db
from hashids import Hashids
from datetime import datetime


# Define models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    active = db.Column(db.Boolean)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    active_sessions = db.Column(db.Integer, default=0)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    requested_rels = db.relationship(
        'Relationship',
        foreign_keys='relationships.requesting_user_id',
        backref='requesting_user'
    )
    received_rels = db.relationship(
        'Relationship',
        foreign_keys='relationships.receiving_user_id',
        backref='receiving_user'
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Relationship(db.Model):
    __tablename__ = 'relationships'
    requesting_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    receiving_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    status = db.Column(db.String(15))


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
    p1_sets = db.Column(db.Integer)
    p2_sets = db.Column(db.Integer)
    p1_legs = db.Column(db.Integer)
    p2_legs = db.Column(db.Integer)
    p1_score = db.Column(db.Integer)
    p2_score = db.Column(db.Integer)
    p1_next_turn = db.Column(db.Boolean)
    status = db.Column(db.String(20))
    type = db.Column(db.Integer)
    match_json = db.Column(db.JSON)
    in_mode = db.Column(db.String(15))
    out_mode = db.Column(db.String(15))
    begin = db.Column(db.DateTime)
    end = db.Column(db.DateTime)

    def set_hashid(self):
        hashids = Hashids(min_length=8)
        self.hashid = hashids.encode(self.id)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Chatmessage(db.Model):
    __tablename__ = 'chatmessages'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime)
