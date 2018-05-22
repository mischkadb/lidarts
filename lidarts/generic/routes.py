from flask import render_template, redirect, url_for
from flask_login import current_user, login_required
from lidarts.generic import bp


@bp.route('/')
def index():
    # logged in users do not need the index page
    if current_user.is_authenticated:
        return redirect(url_for('generic.lobby'))
    return render_template('generic/index.html')


@bp.route('/lobby')
@login_required
def lobby():
    return render_template('generic/lobby.html')