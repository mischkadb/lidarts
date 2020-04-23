from flask import render_template, redirect, url_for, jsonify, request, flash
from flask_babelex import lazy_gettext, gettext
from lidarts.game import bp
from lidarts.game.forms import CreateCricketGameForm, CreateX01GameForm, ScoreForm, GameChatmessageForm, WebcamConsentForm
from lidarts.models import CricketGame, Game, User, Notification, ChatmessageIngame, X01Presetting, UserSettings, Tournament, WebcamSettings
from lidarts import db
from lidarts.socket.public_challenge_handler import broadcast_public_challenges
from lidarts.socket.utils import broadcast_game_aborted, broadcast_new_game, send_notification
from lidarts.game.cricket.prepare_form import prepare_cricket_form
from lidarts.game.cricket.save_preset import save_cricket_preset
from lidarts.game.X01.prepare_form import prepare_x01_form
from lidarts.game.X01.save_preset import save_x01_preset
from lidarts.game.utils import get_name_by_id, collect_statistics, get_player_names, cricket_leg_default
from lidarts.socket.X01_game_handler import start_game
from flask_login import current_user, login_required
from datetime import datetime
import json
import secrets
from sqlalchemy import func


@bp.route('/create', methods=['GET', 'POST'])
@bp.route('/create/<mode>', methods=['GET', 'POST'])
@bp.route('/create/<mode>/<opponent_name>', methods=['GET', 'POST'])
@bp.route('/create/tournament/<tournament_hashid>', methods=['GET', 'POST'])
@bp.route('/create/tournament/<tournament_hashid>/<opponent_name>', methods=['GET', 'POST'])
@login_required
def create(mode='x01', opponent_name=None, tournament_hashid=None):
    if mode == 'x01':
        form = prepare_x01_form(opponent_name, tournament_hashid)
    else:
        form = prepare_cricket_form(opponent_name, tournament_hashid)        

    webcam_query = WebcamSettings.query.filter_by(user=current_user.id).first()
    if not webcam_query or not webcam_query.activated:
        if form.webcam.data:
            return redirect(url_for('game.webcam_consent'))
        form.webcam.render_kw = {'disabled': 'disabled'}

    if form.validate_on_submit():
        player1 = current_user.id if current_user.is_authenticated else None
        if player1 and form.opponent.data == 'local':
            player2 = current_user.id
            status = 'started'
        elif player1 and form.opponent.data == 'online':
            if form.opponent_name.data:
                if form.public_challenge.data:
                    # Public challenge flag and player name specified is not allowed
                    flash(gettext('Public challenges must be created without an opponent name.'), 'danger')
                    return render_template('game/create_game.html', form=form, opponent_name=opponent_name,
                           title=lazy_gettext('Create Game'))
                player2 = (
                    User.query
                    .with_entities(User.id)
                    .filter(func.lower(User.username) == func.lower(form.opponent_name.data))
                    .first_or_404()
                )

                player2_settings = UserSettings.query.filter_by(user=player2.id).first()
                if player2_settings and not player2_settings.allow_challenges:
                    # player 2 does not allow challenge requests
                    flash(gettext('Player does not allow challenges'), 'danger')
                    return render_template('game/create_game.html', form=form, opponent_name=opponent_name,
                           title=lazy_gettext('Create Game'))

                message = gettext('New challenge')
                notification = Notification(user=player2, message=message, author=current_user.username,
                                            type='challenge')
                db.session.add(notification)
                send_notification(form.opponent_name.data, message, current_user.username, 'challenge', webcam=form.webcam.data)
            else:
                player2 = None
            status = 'challenged'
        else:
            # computer as opponent
            player2 = None
            status = 'started'

        if form.webcam.data:
            if player2:
                webcam_player2 = WebcamSettings.query.filter_by(user=player2).first()
                if not webcam_player2 or not webcam_player2.activated:
                    flash(gettext('Player 2 does not have webcam games enabled.'), 'danger')
                    return render_template('game/create_game.html', form=form, opponent_name=opponent_name,
                            title=lazy_gettext('Create Game'))

            jitsi_hashid = secrets.token_urlsafe(8)[:8]
        else:
            jitsi_hashid = None

        tournament = form.tournament.data if form.tournament.data != '-' else None

        if mode == 'x01':
            match_json = json.dumps({1: {1: {1: {'scores': [], 'double_missed': []},
                                         2: {'scores': [], 'double_missed': []}}}})
            game = Game(
                player1=player1, player2=player2, type=form.type.data,
                variant='x01',
                bo_sets=form.bo_sets.data, bo_legs=form.bo_legs.data,
                two_clear_legs=form.two_clear_legs.data,
                p1_sets=0, p2_sets=0, p1_legs=0, p2_legs=0,
                p1_score=int(form.type.data), p2_score=int(form.type.data),
                in_mode=form.in_mode.data, out_mode=form.out_mode.data,
                begin=datetime.utcnow(), match_json=match_json,
                status=status, opponent_type=form.opponent.data,
                public_challenge=form.public_challenge.data,
                tournament=tournament, 
                score_input_delay=form.score_input_delay.data,
                webcam=form.webcam.data, jitsi_hashid=jitsi_hashid,
                )
        elif mode == 'cricket':
            match_json = json.dumps(
                {
                    1: {
                        1: cricket_leg_default.copy(),
                    },
                },
            )
            game = CricketGame(
                player1=player1, player2=player2, variant='cricket',
                bo_sets=form.bo_sets.data, bo_legs=form.bo_legs.data,
                two_clear_legs=form.two_clear_legs.data,
                p1_sets=0, p2_sets=0, p1_legs=0, p2_legs=0,
                p1_score=0, p2_score=0,
                begin=datetime.utcnow(), match_json=match_json,
                status=status, opponent_type=form.opponent.data,
                public_challenge=form.public_challenge.data,
                tournament=tournament, 
                score_input_delay=form.score_input_delay.data,
                webcam=form.webcam.data, jitsi_hashid=jitsi_hashid,
                )
        else:
            pass

        # Preset saving
        if form.save_preset.data:
            if mode == 'x01':
                save_x01_preset(form)
            elif mode == 'cricket':
                save_cricket_preset(form)
            else:
                pass

        if game.opponent_type.startswith('computer'):
            game.opponent_type += form.level.data

        game.p1_next_turn = form.starter.data == 'me'
        if form.starter.data == 'closest_to_bull':
            game.p1_next_turn = True
            closest_to_bull_json = json.dumps({1: [], 2: []})
            game.closest_to_bull_json = closest_to_bull_json
            game.closest_to_bull = True
        db.session.add(game)
        db.session.commit()  # needed to get a game id for the hashid
        game.set_hashid()
        db.session.commit()
        return redirect(url_for('game.start', hashid=game.hashid))
    return render_template('game/create_game.html', form=form,
                           opponent_name=opponent_name, title=lazy_gettext('Create Game'))


@bp.route('/<hashid>/statistics/<set_>/<leg>')
def statistics_set_leg(hashid, set_, leg):
    game = Game.query.filter_by(hashid=hashid).first_or_404()

    player_names = get_player_names(game)

    match_json = json.loads(game.match_json)
    leg_data_json = match_json[set_][leg]

    return render_template('game/X01_statistics.html', playerNames=player_names, leg_data_json=leg_data_json)


@bp.route('/')
@bp.route('/<hashid>')
@bp.route('/<hashid>/<theme>')
def start(hashid, theme=None):
    game = Game.query.filter_by(hashid=hashid).first()
    if not game:
        game = CricketGame.query.filter_by(hashid=hashid).first_or_404()
    # check if we found an opponent, logged in users only
    if game.status == 'challenged' and current_user.is_authenticated and current_user.id != game.player1:
        # Check webcam consent
        if game.webcam:
            webcam_settings = WebcamSettings.query.filter_by(user=current_user.id).first()
            if not webcam_settings or not webcam_settings.activated:
                return redirect(url_for('game.webcam_consent'))

        if not game.player2 or game.player2 == current_user.id:
            game.player2 = current_user.id
            game.status = 'started'
            db.session.commit()
            # send message to global chat
            broadcast_new_game(game)
            # signal the waiting player and spectators
            start_game(hashid)
            broadcast_public_challenges()

    game_dict = game.as_dict()

    player_names = get_player_names(game)

    game_dict['player1_name'] = player_names[0]
    game_dict['player2_name'] = player_names[1]

    match_json = json.loads(game.match_json)

    # for player1 and spectators while waiting
    if game.status == 'challenged':
        if game.public_challenge:
            if not current_user.is_authenticated:
                return redirect(url_for('generic.index'))
            return render_template(
                'game/wait_for_opponent_public_challenge.html',
                game=game_dict,
                title=lazy_gettext('Waiting...'),
                )

        p2_name = get_name_by_id(game.player2) if game.player2 else None
        return render_template(
            'game/wait_for_opponent.html',
            game=game_dict,
            p2_name=p2_name,
            title=lazy_gettext('Waiting...'),
            )
    # for everyone if the game is completed
    if game.status in {'completed', 'aborted', 'declined'}:
        statistics = collect_statistics(game, match_json)
        player_countries = [None, None]
        if game.player1:
            p1_country = UserSettings.query.with_entities(UserSettings.country).filter_by(user=game.player1).first()
            if not p1_country:
                p1_country = UserSettings(user=game.player1)
                db.session.add(p1_country)
                db.session.commit()
                p1_country = None
            else:
                p1_country = p1_country[0]
            player_countries[0] = p1_country
        if game.player2 and game.player1 != game.player2:
            p2_country = UserSettings.query.with_entities(UserSettings.country).filter_by(user=game.player2).first()
            if not p2_country:
                p2_country = UserSettings(user=game.player2)
                db.session.add(p2_country)
                db.session.commit()
                p2_country = None
            else:
                p2_country = p2_country[0]
            player_countries[1] = p2_country

        return render_template(
            f'game/{game.variant}/completed.html',
            game=game_dict,
            match_json=match_json,
            stats=statistics,
            countries=player_countries,
            title=lazy_gettext('Match overview'),
            )

    # for running games
    form = ScoreForm()
    chat_form = GameChatmessageForm()
    chat_form_small = GameChatmessageForm()
    caller = 'default'
    cpu_delay = current_user.cpu_delay if current_user.is_authenticated else 0

    user = current_user.id if current_user.is_authenticated else None

    if user in {game.player1, game.player2}:
        messages = ChatmessageIngame.query.filter_by(game_hashid=game.hashid).order_by(ChatmessageIngame.id.asc()).all()
    else:
        messages = []

    if user:
        settings = UserSettings.query.filter_by(user=user).first()
        if not settings:
            settings = UserSettings(user=user)
            db.session.add(settings)
            db.session.commit(settings)
        caller = settings.caller
    else:
        settings = {'checkout_suggestions': False}

    user_names = {}
    for message in messages:
        user_names[message.author] = (
            User.query
            .with_entities(User.username)
            .filter_by(id=message.author)
            .first_or_404()[0]
        )

    if theme:
        title = lazy_gettext('Stream overlay')
    else:
        title = lazy_gettext('Live Match')

    stream_consent = True
    channel_ids = [None, None]
    if game.webcam and current_user.is_authenticated and current_user.id in (game.player1, game.player2):
        # webcam base template
        template = 'webcam'
        webcam_settings = WebcamSettings.query.filter_by(user=current_user.id).first()
        if webcam_settings and webcam_settings.force_scoreboard_page:
            # force normal game template
            template = 'game'
        p1_webcam_settings = WebcamSettings.query.filter_by(user=game.player1).first()
        p2_webcam_settings = WebcamSettings.query.filter_by(user=game.player2).first() if game.player2 else None
        if not p1_webcam_settings.stream_consent or (p2_webcam_settings and not p2_webcam_settings.stream_consent):
            stream_consent = False
    else:
        if game.webcam:
            p1_webcam_settings = WebcamSettings.query.filter_by(user=game.player1).first()
            p2_webcam_settings = WebcamSettings.query.filter_by(user=game.player2).first() if game.player2 else None
            p1_user_settings = UserSettings.query.filter_by(user=game.player1).first()
            p2_user_settings = UserSettings.query.filter_by(user=game.player2).first() if game.player2 else None
            if (
                p1_webcam_settings.stream_consent and p2_webcam_settings and p2_webcam_settings.stream_consent
                and (p1_user_settings.channel_id or p1_user_settings.channel_id)
            ):
                # consent was given by both players, render watch page
                template = 'watch_webcam'
                channel_ids[0] = p1_user_settings.channel_id
                channel_ids[1] = p2_user_settings.channel_id
            else:
                # no consent for spectators
                template = 'game'
            webcam_settings = None
        else:
            template = 'game'
            webcam_settings = None

    return render_template(f'game/{game.variant}/{template}.html', game=game_dict, form=form, match_json=match_json,
                            caller=caller, cpu_delay=cpu_delay, title=title,
                            chat_form=chat_form, chat_form_small=chat_form_small,
                            messages=messages, user_names=user_names,
                            stream=theme, channel_ids=channel_ids,
                            settings=settings, webcam_settings=webcam_settings,
                            stream_consent=stream_consent,
                            )


@bp.route('/decline_challenge/')
@bp.route('/decline_challenge/<id_>', methods=['POST'])
def decline_challenge(id_):
    id_ = int(id_)
    game = Game.query.filter_by(id=id_).first_or_404()
    if game.status != 'challenged':
        return jsonify('success')
    game.status = "declined"
    game.end = datetime.utcnow()
    db.session.commit()
    return jsonify('success')


@bp.route('/cancel_challenge/<hashid>')
def cancel_challenge(hashid):
    game = Game.query.filter_by(hashid=hashid).first_or_404()
    if game.status != 'challenged':
        return redirect(url_for('generic.lobby'))
    game.status = "declined"
    game.end = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('generic.lobby'))


@bp.route('/abort_game/')
@bp.route('/abort_game/<hashid>', methods=['POST'])
def abort_game(hashid):
    game = Game.query.filter_by(hashid=hashid).first()
    if not game:
        game = CricketGame.query.filter_by(hashid=hashid).first_or_404()
    if game.status == 'completed':
        return redirect(url_for('generic.lobby'))
    game.status = "aborted"
    game.end = datetime.utcnow()
    broadcast_game_aborted(game)
    db.session.commit()
    return redirect(url_for('generic.lobby'))


@bp.route('/webcam_consent', methods=['GET', 'POST'])
@login_required
def webcam_consent():
    webcam_query = WebcamSettings.query.filter_by(user=current_user.id).first()
    if webcam_query and webcam_query.activated:
        return redirect(url_for('game.create', webcam=True))
    form = WebcamConsentForm()
    if form.validate_on_submit():
        if webcam_query:
            webcam_query.activated = True
            webcam_query.stream_consent = form.stream_consent.data
        else:
            webcam_consent = WebcamSettings(
                user=current_user.id,
                activated=True,
                stream_consent=form.stream_consent.data
            )
            db.session.add(webcam_consent)
        db.session.commit()
        return redirect(url_for('game.create', webcam=True))
    return render_template('game/webcam_consent.html', form=form)


@bp.route('/webcam_follow', methods=['GET', 'POST'])
@login_required
def webcam_follow():
    webcam_settings = WebcamSettings.query.filter_by(user=current_user.id).first()
    if not webcam_settings or not webcam_settings.activated or not webcam_settings.mobile_follower_mode:
        return redirect(url_for('game.create', webcam=False))
    
    
    return render_template(
        'game/x01/webcam_follow.html',
        webcam_settings=webcam_settings,        
    )
