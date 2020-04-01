from flask import Blueprint

bp = Blueprint('tournament', __name__, url_prefix='/tournament')

from lidarts.tournament import routes
