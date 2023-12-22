from flask import Blueprint

bp = Blueprint('openvidu', __name__, url_prefix='/openvidu')

from lidarts.openvidu import routes
