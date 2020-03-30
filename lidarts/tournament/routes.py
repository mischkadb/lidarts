from flask import render_template, url_for, redirect, flash, current_app, request
from flask_babelex import lazy_gettext
from flask_login import current_user, login_required
from lidarts import db, socketio
from lidarts.tournament.forms import CreateTournamentForm
from lidarts.tournament import bp
from lidarts.models import Tournament


@bp.route('/overview', methods=['GET', 'POST'])
@login_required
def overview():
    form = CreateTournamentForm()

    if form.validate_on_submit():
        pass

    return render_template(
        'tournament/overview.html',
        form=form,
        title=lazy_gettext('Tournaments'),
    )


@bp.route('/<hashid>')
@login_required
def details(hashid):
    return render_template('tournament/details.html', title=lazy_gettext('Tournament details'))
