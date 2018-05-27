from flask import render_template, redirect, url_for
from flask_login import current_user, login_required
from lidarts import db
from lidarts.generic import bp
from datetime import datetime


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/')
def index():
    # logged in users do not need the index page
    if current_user.is_authenticated:
        return redirect(url_for('generic.lobby'))
    return render_template('generic/index.html')


@bp.route('/about')
def about():
    return render_template('generic/index.html')


@bp.route('/lobby')
@login_required
def lobby():
    return render_template('generic/lobby.html')