from gevent import monkey
monkey.patch_all()

import babel
from dotenv import load_dotenv
import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore
from flask_socketio import SocketIO
from flask_mail import Mail
from flask_moment import Moment
from flask_babelex import Babel
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask._compat import text_type
from flask.json import JSONEncoder as BaseEncoder

from speaklater import _LazyString
from sqlalchemy import MetaData


# disable false positive pylint warning - https://github.com/PyCQA/pylint/issues/414
class JSONEncoder(BaseEncoder):
    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, _LazyString):
            return text_type(o)

        return BaseEncoder.default(self, o)


convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
mail = Mail()
security = Security()
socketio = SocketIO()
babelobject = Babel()
moment = Moment()

avatars = UploadSet('avatars', IMAGES)


# Fixes bug: url_for generates http endpoints instead of https which causes mixed-content-errors
class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


def format_datetime(value):
    return babel.dates.format_datetime(value, "dd.MM.y HH:mm")


def create_app(test_config=None):
    # Create Flask app with a default config
    app = Flask(__name__, instance_relative_config=True)

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
    from lidarts.auth.forms import ExtendedLoginForm, ExtendedRegisterForm, \
        ExtendedChangePasswordForm, ExtendedResetPasswordForm

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore,
                      login_form=ExtendedLoginForm,
                      register_form=ExtendedRegisterForm,
                      change_password_form=ExtendedChangePasswordForm,
                      reset_password_form=ExtendedResetPasswordForm)
    socketio.init_app(app, message_queue='redis://', async_mode='gevent',
                      cors_allowed_origins=['https://lidarts.org', 'https://beta.lidarts.org',
                                            'http://127.0.0.1:5000'])
    babelobject.init_app(app)
    moment.init_app(app)
    configure_uploads(app, avatars)
    patch_request_class(app, 2 * 1024 * 1024)

    app.json_encoder = JSONEncoder
    # Fixes bug: url_for generates http endpoints instead of https which causes mixed-content-errors
    app.wsgi_app = ReverseProxied(app.wsgi_app)

    # filter for jinja
    app.jinja_env.filters['datetime'] = format_datetime

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

    from lidarts.tools import bp as tools_bp
    app.register_blueprint(tools_bp)

    from lidarts.statistics import bp as statistics_bp
    app.register_blueprint(statistics_bp)

    from lidarts.generic.errors import not_found_error, internal_error
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_error)

    import lidarts.models
    import lidarts.socket.base_handler
    import lidarts.socket.chat_handler
    import lidarts.socket.X01_game_handler

    return app


@babelobject.localeselector
def get_locale():
    return request.accept_languages.best_match(['de', 'en'])


