from flask import Blueprint

bp = Blueprint('statistics', __name__, url_prefix='/statistics')

from lidarts.statistics import routes