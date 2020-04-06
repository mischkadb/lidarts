from flask import render_template, url_for, redirect, flash, current_app, request
from flask_babelex import lazy_gettext
from flask_login import current_user, login_required
from lidarts import db, socketio
from lidarts.generic.forms import ChatmessageForm
from lidarts.tournament import bp
from lidarts.tournament.forms import CreateTournamentForm
from lidarts.models import Game, Tournament, Chatmessage, User, UserSettings, UserStatistic
from datetime import datetime, timedelta
from sqlalchemy.orm import aliased


def handle_form(form, update=False, tournament=None):
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

    if update:
        tournament.name = form.name.data
        tournament.public = form.public_tournament.data
        tournament.description = form.description.data
        tournament.external_url = form.external_url.data
        tournament.start_timestamp = start_timestamp
        flash(lazy_gettext('Tournament updated.'), 'success')

    else:
        tournament = Tournament(
            name=form.name.data,
            description=form.description.data,
            public=form.public_tournament.data,
            external_url=form.external_url.data,
            start_timestamp=start_timestamp,
            creator=current_user.id,
        )
        db.session.add(tournament)
        current_user.tournaments.append(tournament)

    db.session.commit()

    return tournament


@bp.route('/overview', methods=['GET', 'POST'])
@login_required
def overview():
    form = CreateTournamentForm()

    if form.validate_on_submit():
        tournament = handle_form(form)
        if tournament:
            return redirect(url_for('tournament.details', hashid=tournament.hashid))

    upcoming_tournaments = (
        Tournament.query
        .filter_by(public=True)
        .filter(Tournament.start_timestamp > datetime.utcnow())
        .order_by(Tournament.start_timestamp)
        .all()
    )

    player_tournaments = (
        Tournament.query
        .filter_by(creator=current_user.id)
        .all()
    )

    return render_template(
        'tournament/overview.html',
        form=form,
        player_tournaments=player_tournaments,
        upcoming_tournaments=upcoming_tournaments,
        title=lazy_gettext('Tournaments'),
    )


@bp.route('/<hashid>')
@login_required
def details(hashid):
    tournament, creator_name = (
        Tournament.query
        .filter_by(hashid=hashid)
        .join(User, User.id == Tournament.creator).add_columns(User.username)
        .first_or_404()
    )

    form = ChatmessageForm()
    messages = (
        Chatmessage.query
        .filter_by(tournament_hashid=hashid)
        .filter(Chatmessage.timestamp > (datetime.utcnow() - timedelta(hours=24)))
        .order_by(Chatmessage.id.desc())
        .join(User).add_columns(User.username)
        .join(UserStatistic).add_columns(UserStatistic.average)
        .join(UserSettings).add_columns(UserSettings.country)
        .limit(100)
        .all()
    )

    in_tournament = tournament in current_user.tournaments

    player1 = aliased(User)
    player2 = aliased(User)
    recent_results = (
        Game.query
        .filter_by(tournament=hashid)
        .filter_by(status='completed')
        .join(player1, Game.player1 == player1.id).add_columns(player1.username)
        .join(player2, Game.player2 == player2.id, isouter=True).add_columns(player2.username)
        .order_by(Game.end.desc())
        .limit(10)
        .all()
    )

    settings = UserSettings.query.filter_by(user=current_user.id).first()
    if not settings:
        settings = UserSettings(user=current_user.id)
        db.session.add(settings)
        db.session.commit()

    for game, _, _ in recent_results:
        if game.bo_sets > 1:
            game.p1_final_score = game.p1_sets
            game.p2_final_score = game.p2_sets
        else:
            game.p1_final_score = game.p1_legs
            game.p2_final_score = game.p2_legs

    return render_template(
        'tournament/details.html',
        tournament=tournament,
        form=form,
        messages=messages,
        in_tournament=in_tournament,
        recent_results=recent_results,
        creator_name=creator_name,
        show_average_in_chat_list=settings.show_average_in_chat_list,
        title=lazy_gettext('Tournament details'),
    )


@bp.route('/<hashid>/settings', methods=['GET', 'POST'])
@login_required
def settings(hashid):
    form = CreateTournamentForm()
    tournament = Tournament.query.filter_by(hashid=hashid).first_or_404()
    if tournament.creator != current_user.id:
        return redirect(url_for('tournament.details', hashid=hashid))

    if form.validate_on_submit():
        handle_form(form, update=True, tournament=tournament)

    else:
        form.name.data = tournament.name
        form.public_tournament.data = tournament.public
        form.description.data = tournament.description
        form.external_url.data = tournament.external_url
        if tournament.start_timestamp:
            form.start_date.data = datetime.date(tournament.start_timestamp)
            form.start_time.data = datetime.time(tournament.start_timestamp)

    return render_template(
        'tournament/settings.html',
        form=form,
        tournament=tournament,
        title=lazy_gettext('Tournament settings'),
    )
