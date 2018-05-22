from lidarts.models import User


def register(client, username, password, confirm_password, email):
    return client.post(
        '/register', data=dict(
            username=username,
            password=password,
            confirm_password=confirm_password,
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
    confirm_password = 'pass'
    email = 'test@test.'

    # test all error messages
    response = register(client, username, password, confirm_password, email)
    assert b'Field must be between 3 and 20 characters long.' in response.data
    assert b'Invalid email address.' in response.data
    assert b'Field must be between 6 and 50 characters long.' in response.data
    assert b'Passwords do not match.' in response.data

    # test successful registration
    response = register(client, username + 'c', password + 'd', confirm_password + 'wd', email + 'de')
    assert b'Welcome to lidarts abc. Thank you for registering.' in response.data

    # test taken name and email
    response = register(client, username + 'c', password + 'd', confirm_password + 'wd', email + 'de')
    assert b'Username is already taken.' in response.data
    assert b'Email address is already in use.' in response.data

    # test that the user was inserted into the database
    with app.app_context():
        assert User.query.filter_by(username='abc').first() is not None


def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password,
        submit=True
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def test_login(client, db_session):
    username = 'test'
    password = 'passwd'

    # create a dummy user
    user = User(username=username, email='test@test.de')
    user.set_password(password)
    db_session.add(user)
    db_session.commit()

    # test that viewing the page renders without template errors
    assert client.get('/login').status_code == 200

    response = login(client, username, password)
    assert b'You successfully logged in.' in response.data

    response = logout(client)
    assert b'Logout successful.' in response.data

    response = login(client, username + 'x', password)
    assert b'Invalid username or password.' in response.data

    response = login(client, username, password + 'x')
    assert b'Invalid username or password.' in response.data


