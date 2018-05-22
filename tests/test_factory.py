from lidarts import create_app


# Test create_app without passing test config.
def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing



