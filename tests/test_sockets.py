from lidarts.socket.game_handler import current_turn_user_id
from lidarts.models import User


def test_init(socket_client, db_session, game):
    socket_client.get_received('/game')
    socket_client.emit('init', {'hashid': game.hashid}, namespace='/game')
    received = socket_client.get_received('/game')
    assert len(received) == 1
    assert received[0]['name'] == 'score_response'
    assert received[0]['args'][0]['p1_score'] == received[0]['args'][0]['p2_score'] == 170


def test_send_score(socket_client, db_session, game):
    # get both players
    user = User.query.filter_by(id=game.player1).first()
    user2 = User.query.filter_by(id=game.player2).first()

    # connect to room
    socket_client.emit('init', {'hashid': game.hashid}, namespace='/game')
    socket_client.get_received('/game')

    # test basic scoring
    socket_client.emit('send_score', {'score': 80, 'hashid': game.hashid, 'user_id': user.id}, namespace='/game')
    received = socket_client.get_received('/game')
    assert len(received) == 1
    assert received[0]['args'][0]['p1_score'] == 90
    assert received[0]['args'][0]['p2_score'] == 170
    assert received[0]['args'][0]['p1_next_turn'] is False

    # test wrong id, should not score
    socket_client.emit('send_score', {'score': 80, 'hashid': game.hashid, 'user_id': user.id}, namespace='/game')
    received = socket_client.get_received('/game')
    assert len(received) == 0

    # test leg win
    socket_client.emit('send_score', {'score': 170, 'hashid': game.hashid, 'user_id': user2.id}, namespace='/game')
    received = socket_client.get_received('/game')
    assert len(received) == 1
    assert received[0]['args'][0]['p1_score'] == 170
    assert received[0]['args'][0]['p2_score'] == 170
    assert received[0]['args'][0]['p1_legs'] == 0
    assert received[0]['args'][0]['p2_legs'] == 1
    assert received[0]['args'][0]['p1_next_turn'] is False

    # test set win and correct leg starting player
    socket_client.emit('send_score', {'score': 170, 'hashid': game.hashid, 'user_id': user2.id}, namespace='/game')
    received = socket_client.get_received('/game')
    assert len(received) == 1
    assert received[0]['args'][0]['p1_score'] == 170
    assert received[0]['args'][0]['p2_score'] == 170
    assert received[0]['args'][0]['p1_legs'] == 0
    assert received[0]['args'][0]['p2_legs'] == 0
    assert received[0]['args'][0]['p1_sets'] == 0
    assert received[0]['args'][0]['p2_sets'] == 1
    assert received[0]['args'][0]['p1_next_turn'] is True

    # test double out bust
    socket_client.emit('send_score', {'score': 169, 'hashid': game.hashid, 'user_id': user.id}, namespace='/game')
    received = socket_client.get_received('/game')
    assert len(received) == 1
    assert received[0]['args'][0]['p1_score'] == 170
    assert received[0]['args'][0]['p1_next_turn'] is False

    # another leg win
    socket_client.emit('send_score', {'score': 170, 'hashid': game.hashid, 'user_id': user2.id}, namespace='/game')
    received = socket_client.get_received('/game')
    assert len(received) == 1
    assert received[0]['args'][0]['p1_legs'] == 0
    assert received[0]['args'][0]['p2_legs'] == 1
    assert received[0]['args'][0]['p1_sets'] == 0
    assert received[0]['args'][0]['p2_sets'] == 1
    assert received[0]['args'][0]['p1_next_turn'] is False

    # test game win
    socket_client.emit('send_score', {'score': 170, 'hashid': game.hashid, 'user_id': user2.id}, namespace='/game')
    received = socket_client.get_received('/game')
    assert len(received) == 2
    assert received[0]['args'][0]['p1_sets'] == 0
    assert received[0]['args'][0]['p2_sets'] == 2
    assert received[1]['name'] == 'game_completed'

