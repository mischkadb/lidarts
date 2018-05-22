import pytest
import os
import sqlalchemy as sa
from lidarts import create_app, db as _db


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
