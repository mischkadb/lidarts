from flask import render_template, url_for, redirect, flash, current_app, request
from flask_babelex import lazy_gettext
from flask_login import current_user, login_required
from lidarts import db, socketio
from lidarts.generic.forms import ChatmessageForm
from lidarts.tournament import bp
from lidarts.tournament.bracket_generator import generate_bracket
from lidarts.tournament.forms import CreateTournamentForm, ConfirmStreamGameForm, CloseRegistrationForm, TournamentPreparationForm
from lidarts.models import Game, GameBase, Tournament, Chatmessage, User, UserSettings, UserStatistic, WebcamSettings, StreamGame, TournamentStage, X01TournamentStageRound
from datetime import datetime, timedelta
from sqlalchemy.orm import aliased
import secrets
import math


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

    managed_externally = not form.automatic_management.data
    if update:
        tournament.name = form.name.data
        tournament.public = form.public_tournament.data
        tournament.description = form.description.data
        tournament.external_url = form.external_url.data
        tournament.start_timestamp = start_timestamp
        tournament.registration_open = form.registration_open.data
        tournament.registration_apply = form.registration_apply.data
        tournament.managed_externally = managed_externally
        if not tournament.managed_externally and not tournament.stages:
            stage = TournamentStage(
                format=form.tournament_format.data
            )
            tournament.stages.append(stage)
        elif not tournament.managed_externally:
            tournament.stages[0].format = form.tournament_format.data

        flash(lazy_gettext('Tournament updated.'), 'success')

    else:
        tournament = Tournament(
            name=form.name.data,
            description=form.description.data,
            public=form.public_tournament.data,
            external_url=form.external_url.data,
            start_timestamp=start_timestamp,
            creator=current_user.id,
            managed_externally=managed_externally,
        )
        if not tournament.managed_externally and not tournament.stages:
            stage = TournamentStage(
                format=form.tournament_format.data
            )
            tournament.stages.append(stage)
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

    usernames = {}

    for player in tournament.players:
        if player.username not in usernames:
            usernames[player.id] = player.username

    if current_user in tournament.banned_players:
        flash(lazy_gettext('You were banned from this tournament.'), 'danger')
        return redirect(url_for('generic.lobby'))

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
        GameBase.query
        .filter_by(tournament=hashid)
        .filter_by(status='completed')
        .join(player1, GameBase.player1 == player1.id).add_columns(player1.username)
        .join(player2, GameBase.player2 == player2.id, isouter=True).add_columns(player2.username)
        .order_by(GameBase.end.desc())
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

    template = 'details' if tournament.status != 'started' else 'bracket'

    return render_template(
        f'tournament/{template}.html',
        tournament=tournament,
        usernames=usernames,
        form=form,
        messages=messages,
        in_tournament=in_tournament,
        recent_results=recent_results,
        creator_name=creator_name,
        show_average_in_chat_list=settings.show_average_in_chat_list,
        country=settings.country,
        title=lazy_gettext('Tournament details'),
    )


@bp.route('/<hashid>/settings', methods=['GET', 'POST'])
@login_required
def settings(hashid):
    form = CreateTournamentForm()
    close_registration_form = CloseRegistrationForm()

    tournament = Tournament.query.filter_by(hashid=hashid).first_or_404()
    if tournament.creator != current_user.id:
        return redirect(url_for('tournament.details', hashid=hashid))

    if form.validate_on_submit():
        handle_form(form, update=True, tournament=tournament)
    elif close_registration_form.validate_on_submit():
        return redirect(url_for('tournament.close_registration', hashid=tournament.hashid))
    else:
        form.name.data = tournament.name
        form.public_tournament.data = tournament.public
        form.description.data = tournament.description
        form.external_url.data = tournament.external_url
        form.registration_open.data = tournament.registration_open
        form.automatic_management.data = not tournament.managed_externally
        if tournament.start_timestamp:
            form.start_date.data = datetime.date(tournament.start_timestamp)
            form.start_time.data = datetime.time(tournament.start_timestamp)

    return render_template(
        'tournament/settings.html',
        form=form,
        tournament=tournament,
        close_registration_form=close_registration_form,
        title=lazy_gettext('Tournament settings'),
    )


@bp.route('/close_registration/<hashid>')
@login_required
def close_registration(hashid):
    tournament = Tournament.query.filter_by(hashid=hashid).first_or_404()
    if tournament.creator != current_user.id or tournament.status != 'registration':
        return redirect(url_for('tournament.details', hashid=tournament.hashid))
    tournament.status = 'preparation'

    num_players = len(tournament.players)
    num_rounds_upper = math.ceil(math.log2(num_players))
    for round_ in range(num_rounds_upper):
        tournament_round = X01TournamentStageRound(name_=f'ub r{round_+1}')
        tournament.stages[0].rounds.append(tournament_round)

    num_rounds_lower = 0 if tournament.stages[0].format == 'single_elim' else math.ceil(math.log2(num_players / 2)) * 2
    for round_ in range(num_rounds_lower):
        tournament_round = X01TournamentStageRound(name_=f'lb r{round_+1}')
        tournament.stages[0].rounds.append(tournament_round)

    if tournament.stages[0].format == 'double_elim_rematch':
        tournament_round = X01TournamentStageRound(name_=f'gf1')
        tournament.stages[0].rounds.append(tournament_round)
        tournament_round = X01TournamentStageRound(name_=f'gf2')
        tournament.stages[0].rounds.append(tournament_round)
    
    if tournament.stages[0].format == 'double_elim_no_rematch':
        tournament_round = X01TournamentStageRound(name_=f'gf')
        tournament.stages[0].rounds.append(tournament_round)

    db.session.commit()

    return redirect(url_for('tournament.preparation', hashid=tournament.hashid))


@bp.route('/preparation/<hashid>', methods=['GET', 'POST'])
@login_required
def preparation(hashid):
    tournament = Tournament.query.filter_by(hashid=hashid).first_or_404()
    if tournament.creator != current_user.id or tournament.status != 'preparation':
        return redirect(url_for('tournament.details', hashid=tournament.hashid))

    tournament_round_form = TournamentPreparationForm()

    if tournament_round_form.validate_on_submit():
        for form_round, stage_round in zip(tournament_round_form.rounds, tournament.stages[0].rounds):
            stage_round.bo_sets = form_round.bo_sets.data
            stage_round.bo_legs = form_round.bo_legs.data
            stage_round.two_clear_legs = form_round.two_clear_legs.data
            stage_round.starter = form_round.starter.data
            stage_round.score_input_delay = form_round.score_input_delay.data
            stage_round.type_ = form_round.type_.data
            stage_round.in_mode = form_round.in_mode.data
            stage_round.out_mode = form_round.out_mode.data
        db.session.commit()
        player_id_list = [int(player_id) for player_id in tournament_round_form.player_list.data.split(',')]
        generate_bracket(player_id_list, tournament)
        return redirect(url_for('tournament.details', hashid=tournament.hashid))
    else:    
        tournament_rounds = []
        tournament_round_form.rounds.pop_entry()
        for tournament_round in tournament.stages[0].rounds:
            tournament_round_form.rounds.append_entry(tournament_round)

    return render_template(
        'tournament/preparation.html',
        tournament=tournament,
        tournament_round_form=tournament_round_form,
        title=lazy_gettext('Tournament preparation'),
    )


@bp.route('/<hashid>/stream', methods=['GET', 'POST'])
@login_required
def stream(hashid):
    form = ConfirmStreamGameForm()

    tournament = Tournament.query.filter_by(hashid=hashid).first_or_404()
    if tournament.creator != current_user.id:
        return redirect(url_for('tournament.details', hashid=hashid))

    games = (
        Game.query
        .filter_by(tournament=hashid)
        .filter_by(webcam=True)
        .filter_by(status='started')
        .all()
    )
    streamable_games = {}
    user_names = {}
    choices = []

    for game in games:
        player1 = WebcamSettings.query.filter_by(user=game.player1).first()
        if not player1 or not player1.stream_consent:
            continue
        player2 = WebcamSettings.query.filter_by(user=game.player2).first()
        if not player2 or not player2.stream_consent:
            continue
        if game.player1 not in user_names:
            user_names[game.player1] = (
                User.query
                .with_entities(User.username)
                .filter_by(id=game.player1)
                .first_or_404()[0]
            )
        if game.player2 and game.player1 != game.player2 and game.player2 not in user_names:
            user_names[game.player2] = (
                User.query
                .with_entities(User.username)
                .filter_by(id=game.player2)
                .first_or_404()[0]
            )
        streamable_games[game.hashid] = game
        choices.append((game.hashid, game.hashid))

    streamed_game = StreamGame.query.filter_by(user=current_user.id).first()
    streamed_game = streamed_game.hashid if streamed_game else None
    form.games.choices = choices

    if form.validate_on_submit():
        streamed_game = StreamGame.query.filter_by(user=current_user.id).first()
        if not streamed_game:
            streamed_game = StreamGame(user=current_user.id)
            db.session.add(streamed_game)
        streamed_game.hashid = form.games.data
        streamed_game.jitsi_hashid = streamable_games[form.games.data].jitsi_hashid
        db.session.commit()
        flash(lazy_gettext('Game selected as stream game.'), 'success')

    return render_template(
        'tournament/stream.html',
        tournament=tournament,
        games=streamable_games,
        user_names=user_names,
        form=form,
        title=lazy_gettext('Tournament streaming'),
    )


@bp.route('/<hashid>/new-api-key')
@login_required
def new_api_key(hashid):
    tournament = Tournament.query.filter_by(hashid=hashid).first_or_404()
    if tournament.creator != current_user.id:
        return redirect(url_for('tournament.details', hashid=hashid))

    tournament.api_key = secrets.token_urlsafe(16)[:16]
    db.session.commit()

    return tournament.api_key
