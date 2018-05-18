from flask import Blueprint

bp = Blueprint('profile', __name__)

from lidarts.profile import routes
