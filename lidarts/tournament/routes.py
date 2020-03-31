from flask import render_template, url_for, redirect, flash, current_app, request
from flask_babelex import lazy_gettext
from flask_login import current_user, login_required
from lidarts import db, socketio
from lidarts.tournament import bp
from lidarts.tournament.forms import CreateTournamentForm
from lidarts.models import Tournament
from datetime import datetime, timedelta


def handle_form(form):
    start_timestamp = None
    if form.public_tournament.data:
        start_timestamp = datetime.combine(
            form.start_date.data, form.start_time.data,
        )
        if start_timestamp < datetime.utcnow():
            flash(lazy_gettext('Start in the past is not allowed for public tournaments.'), 'danger')
            return

        if start_timestamp > datetime.utcnow() + timedelta(days=30):
            flash(lazy_gettext('Start must be within the next 30 days.'), 'danger')
            return

    tournament = Tournament(
        name=form.name.data,
        description=form.description.data,
        public=form.public_tournament.data,
        external_link=form.external_link.data,
        start_timestamp=start_timestamp,
    )
    db.session.add(tournament)
    # db.session.commit()


@bp.route('/overview', methods=['GET', 'POST'])
@login_required
def overview():
    form = CreateTournamentForm()

    if form.validate_on_submit():
        handle_form(form)
        print('test')

    upcoming_tournaments = (
        Tournament.query
        .filter_by(public=True)
        .filter(Tournament.start_timestamp > datetime.utcnow())
        .order_by(Tournament.start_timestamp)
        .all()
    )

    return render_template(
        'tournament/overview.html',
        form=form,
        tournaments=upcoming_tournaments,
        title=lazy_gettext('Tournaments'),
    )


@bp.route('/<hashid>')
@login_required
def details(hashid):

    return render_template(
        'tournament/details.html',
        title=lazy_gettext('Tournament details')
    )
