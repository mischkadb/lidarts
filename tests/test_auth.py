from lidarts.models import User


def register(client, username, password, password_confirm, email):
    return client.post(
        '/register', data=dict(
            username=username,
            password=password,
            password_confirm=password_confirm,
            email=email,
            submit=True
        ), follow_redirects=True
    )


def test_register(client, app, db_session):
    # test that viewing the page renders without template errors
    assert client.get('/register').status_code == 200

    # intentionally incorrect dummy user credentials
    username = 'ab'
    password = 'passw'
    password_confirm = 'pass'
    email = 'test@test.'

    # test all error messages
    response = register(client, username, password, password_confirm, email)
    assert b'Field must be between 3 and 20 characters long.' in response.data
    assert b'Invalid email address' in response.data
    assert b'Password must be at least 6 characters' in response.data

    response = register(client, username, password + 'test', password_confirm + 'tests', email)
    assert b'Passwords do not match' in response.data

    # test successful registration
    response = register(client, username + 'c', password + 'd', password_confirm + 'wd', email + 'de')
    assert b'Lobby' in response.data

    client.get('/logout', follow_redirects=True)

    # test taken name and email
    response = register(client, username + 'c', password + 'd', password_confirm + 'wd', email + 'de')
    assert b'Username is already taken' in response.data
    assert b'is already associated with an account.' in response.data

    # test that the user was inserted into the database
    with app.app_context():
        assert User.query.filter_by(username='abc').first() is not None


def login(client, username, password):
    return client.post('/login', data=dict(
        email=username,
        password=password,
        submit=True
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def test_login(client, db_session, user):
    username = 'test@test.de'
    password = 'passwd'

    # test that viewing the page renders without template errors
    assert client.get('/login').status_code == 200

    response = login(client, username, password)
    assert b'Lobby' in response.data

    response = logout(client)
    assert b'Welcome to lidarts.org' in response.data

    response = login(client, username + 'x', password)
    assert b'Specified user does not exist' in response.data

    response = login(client, username, password + 'x')
    assert b'Invalid password' in response.data

    response = login(client, username.upper(), password)
    assert b'Lobby' in response.data


