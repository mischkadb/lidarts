from flask import Blueprint

bp = Blueprint('auth', __name__)

from lidarts.auth import routes
