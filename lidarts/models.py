from flask_security import UserMixin, RoleMixin
from lidarts import db
from hashids import Hashids


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
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User {}>'.format(self.username)


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
