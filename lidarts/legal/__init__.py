from flask import Blueprint

bp = Blueprint('legal', __name__)

from lidarts.legal import routes

