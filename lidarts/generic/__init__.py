from flask import Blueprint

bp = Blueprint('generic', __name__)

from lidarts.generic import routes
