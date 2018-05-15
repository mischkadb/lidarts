from flask import render_template
from lidarts.generic import bp


@bp.route('/')
def index():
    return render_template('generic/index.html')