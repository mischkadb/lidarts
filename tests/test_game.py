from lidarts.models import User, Game
from tests.test_auth import login, logout


def create_game(client, type, opponent, starter, bo_sets, bo_legs, in_mode, out_mode):
    return client.post('/game/create', data=dict(
        type=type, opponent=opponent, starter=starter, bo_sets=bo_sets, bo_legs=bo_legs,
        in_mode=in_mode, out_mode=out_mode, submit=True
    ), follow_redirects=True)


def test_create_game_local(client, app, db_session, user):
    # test that viewing the page renders without template errors
    assert client.get('/game/create').status_code == 200

    login(client, user.username, 'passwd')

    response = create_game(client, 170, 'local', 'me', 3, 3, 'si', 'do')
    assert response.status_code == 200

    game = Game.query.first()
    assert game.player1 is not None

    assert b'Local Guest' in response.data


def test_create_game_online(client, app, db_session, user, user2):
    # test that viewing the page renders without template errors
    assert client.get('/game/create').status_code == 200

    login(client, user.username, 'passwd')

    response = create_game(client, 170, 'online', 'me', 3, 3, 'si', 'do')
    assert response.status_code == 200

    game = Game.query.first()
    assert game.player1 is not None
    assert game.status == 'challenged'
    assert b'Waiting for player 2...' in response.data

    client2 = app.test_client()

    login(client2, user2.username, 'passwd')

    response = client2.get('/game/' + game.hashid)
    assert game.status == 'started'
    assert game.player1 == user.id and game.player2 == user2.id
    assert response.status_code == 200




