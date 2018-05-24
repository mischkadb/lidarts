from lidarts.models import User


def test_user_model(db_session):
    user = User(username='test', email='test@test.de', password='hash')
    db_session.add(user)
    db_session.commit()

    assert user.id > 0

