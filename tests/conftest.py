import pytest
import os
import sqlalchemy as sa
from lidarts import create_app, db as _db
from lidarts.models import User, Game
from datetime import datetime
import json


@pytest.fixture(scope='session')
def app(request):
    test_config = {
        'SECRET_KEY': 'fashlkhasdflkasdf',
        'SQLALCHEMY_DATABASE_URI': 'postgres:///lidarts-testing',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'TESTING': True,
        'WTF_CSRF_ENABLED': False
    }

    app = create_app(test_config)

    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()


@pytest.fixture(scope='function')
def user(db_session):
    user = User(username='test', email='test@test.de')
    user.set_password('passwd')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope='function')
def user2(db_session):
    user = User(username='test2', email='test2@test.de')
    user.set_password('passwd')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope='function')
def game(db_session, user, user2):
    match_json = json.dumps({1: {1: {1: [], 2: []}}})
    game = Game(player1=user.id, player2=user2.id, type=170,
                bo_sets=3, bo_legs=3,
                p1_sets=0, p2_sets=0, p1_legs=0, p2_legs=0,
                p1_score=170, p2_score=170,
                in_mode='si', out_mode='do',
                begin=datetime.now(), match_json=match_json, status='started')
    game.p1_next_turn = True
    db_session.add(game)
    db_session.commit()
    game.set_hashid()
    db_session.commit()
    return game


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    def teardown():
        _db.drop_all()

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.yield_fixture(scope='function')
def db_session(db):
    """
    Creates a new database session for a test. Note you must use this fixture
    if your test connects to db.

    Here we not only support commit calls but also rollback calls in tests,
    :coolguy:.
    """
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    session.begin_nested()

    # session is actually a scoped_session
    # for the `after_transaction_end` event, we need a session instance to
    # listen for, hence the `session()` call
    @sa.event.listens_for(session(), 'after_transaction_end')
    def resetart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            session.expire_all()
            session.begin_nested()

    db.session = session

    yield session

    session.remove()
    transaction.rollback()
    connection.close()
