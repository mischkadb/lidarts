from flask import Blueprint

bp = Blueprint('tools', __name__, url_prefix='/tools')

from lidarts.tools import routes
