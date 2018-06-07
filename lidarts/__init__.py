import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore
from flask_socketio import SocketIO
from flask_mail import Mail
from flask_moment import Moment
from flask_babel import _, Babel
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
security = Security()
socketio = SocketIO()
babel = Babel()
moment = Moment()


def create_app(test_config=None):
    # Create Flask app with a default config
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=None,
        SQLALCHEMY_DATABASE_URI='postgres:///lidarts_db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # Load test config if we are in testing mode
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from lidarts.models import User, Role
    from lidarts.auth.forms import ExtendedLoginForm, ExtendedRegisterForm

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore,
                      login_form=ExtendedLoginForm,
                      register_form=ExtendedRegisterForm)
    socketio.init_app(app)
    babel.init_app(app)
    moment.init_app(app)

    # Load all blueprints
    from lidarts.generic import bp as generic_bp
    app.register_blueprint(generic_bp)

    from lidarts.game import bp as game_bp
    app.register_blueprint(game_bp)

    from lidarts.profile import bp as profile_bp
    app.register_blueprint(profile_bp)

    from lidarts.legal import bp as legal_bp
    app.register_blueprint(legal_bp)

    from lidarts.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from lidarts.generic.errors import not_found_error, internal_error
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_error)

    import lidarts.models
    import lidarts.socket.base_handler
    import lidarts.socket.chat_handler
    import lidarts.socket.X01_game_handler

    return app
