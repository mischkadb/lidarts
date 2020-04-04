from flask import render_template, redirect, url_for, jsonify, request, flash
from flask_babelex import lazy_gettext, gettext
from lidarts.game import bp
from lidarts.game.forms import CreateX01GameForm, ScoreForm, GameChatmessageForm
from lidarts.models import Game, User, Notification, ChatmessageIngame, X01Presetting, UserSettings, Tournament
from lidarts import db
from lidarts.socket.public_challenge_handler import broadcast_public_challenges
from lidarts.socket.utils import broadcast_game_aborted, broadcast_new_game, send_notification
from lidarts.game.utils import get_name_by_id, collect_statistics, get_player_names
from lidarts.socket.X01_game_handler import start_game
from flask_login import current_user, login_required
from datetime import datetime
import json


@bp.route('/create', methods=['GET', 'POST'])
@bp.route('/create/<mode>', methods=['GET', 'POST'])
@bp.route('/create/<mode>/<opponent_name>', methods=['GET', 'POST'])
@bp.route('/create/tournament/<tournament_hashid>', methods=['GET', 'POST'])
@bp.route('/create/tournament/<tournament_hashid>/<opponent_name>', methods=['GET', 'POST'])
@login_required
def create(mode='x01', opponent_name=None, tournament_hashid=None):
    if mode == 'x01':
        preset = X01Presetting.query.filter_by(user=current_user.id).first()
        if not preset:
            preset = X01Presetting(user=current_user.id)
            db.session.add(preset)
            db.session.commit()
        
        if request.args.get('type'):
            x01_type = request.args.get('type') if request.args.get('type') in ['170', '301', '501', '1001'] else '170'
        elif preset.type:
            x01_type = preset.type
        else:
            x01_type = 501

        if request.args.get('starter'):
            starter_short = {
                '1': 'me',
                '2': 'opponent',
                'bull': 'closest_to_bull',
            }
            starter = starter_short[request.args.get('starter')] if request.args.get('starter') in starter_short else 'me'
        elif preset.starter:
            starter = preset.starter
        else:
            starter = 'me'

        if request.args.get('sets'):
            bo_sets = request.args.get('sets')
            try:
                bo_sets = bo_sets if int(bo_sets) < 30 else 1
            except (ValueError, TypeError):
                bo_sets = 1
        elif preset.bo_sets:
            bo_sets = preset.bo_sets
        else:
            bo_sets = 1        

        if request.args.get('legs'):
            bo_legs = request.args.get('legs')
            try:
                bo_legs = bo_legs if int(bo_legs) < 30 else 1
            except (ValueError, TypeError):
                bo_legs = 1
        elif preset.bo_legs:
            bo_legs = preset.bo_legs
        else:
            bo_legs = 5

        if request.args.get('2cl'):
            two_clear_legs = request.args.get('2cl')
        elif preset.two_clear_legs:
            two_clear_legs = preset.two_clear_legs
        else:
            two_clear_legs = False

        level = preset.level if preset.level else 1
        opponent = preset.opponent_type if preset.opponent_type else 'online'

        in_mode = preset.in_mode if preset.in_mode else 'si'
        out_mode = preset.out_mode if preset.out_mode else 'do'
        public_challenge = preset.public_challenge if preset.public_challenge else False

        form = CreateX01GameForm(
            opponent_name=opponent_name,
            opponent=opponent,
            type=x01_type,
            starter=starter,
            bo_sets=bo_sets,
            bo_legs=bo_legs,
            two_clear_legs=two_clear_legs,
            level=level,
            in_mode=in_mode,
            out_mode=out_mode,
            public_challenge=public_challenge,
        )
        tournaments = current_user.tournaments
        tournament_choices = []
        for tournament in tournaments:
            tournament_choices.append((tournament.hashid, tournament.name))
            if tournament_hashid and tournament_hashid == tournament.hashid and request.method == 'GET':
                form.tournament.default = tournament_hashid
                form.process()
        tournament_choices.append(('-', '-'))
        form.tournament.choices = tournament_choices[::-1]
    else:
        pass  # no other game modes yet
    
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
                    return render_template('game/create_X01.html', form=form, opponent_name=opponent_name,
                           title=lazy_gettext('Create Game'))
                player2 = User.query.with_entities(User.id).filter(User.username.ilike(form.opponent_name.data)).first_or_404()

                player2_settings = UserSettings.query.filter_by(user=player2.id).first()
                if player2_settings and not player2_settings.allow_challenges:
                    # player 2 does not allow challenge requests
                    flash(gettext('Player does not allow challenges'), 'danger')
                    return render_template('game/create_X01.html', form=form, opponent_name=opponent_name,
                           title=lazy_gettext('Create Game'))

                message = gettext('New challenge')
                notification = Notification(user=player2, message=message, author=current_user.username,
                                            type='challenge')
                db.session.add(notification)
                send_notification(form.opponent_name.data, message, current_user.username, 'challenge')
            else:
                player2 = None
            status = 'challenged'
        else:
            # computer as opponent
            player2 = None
            status = 'started'

        tournament = form.tournament.data if form.tournament.data != '-' else None

        match_json = json.dumps({1: {1: {1: {'scores': [], 'double_missed': []},
                                         2: {'scores': [], 'double_missed': []}}}})
        game = Game(
            player1=player1, player2=player2, type=form.type.data,
            bo_sets=form.bo_sets.data, bo_legs=form.bo_legs.data,
            two_clear_legs=form.two_clear_legs.data,
            p1_sets=0, p2_sets=0, p1_legs=0, p2_legs=0,
            p1_score=int(form.type.data), p2_score=int(form.type.data),
            in_mode=form.in_mode.data, out_mode=form.out_mode.data,
            begin=datetime.utcnow(), match_json=match_json,
            status=status, opponent_type=form.opponent.data,
            public_challenge=form.public_challenge.data,
            tournament=tournament,
            )

        # Preset saving
        if form.save_preset.data:
            preset = X01Presetting.query.filter_by(user=current_user.id).first()
            if not preset:
                preset = X01Presetting(user=current_user.id)
                db.session.add(preset)
            preset.bo_sets = form.bo_sets.data
            preset.bo_legs = form.bo_legs.data
            preset.two_clear_legs = form.two_clear_legs.data
            preset.starter = form.starter.data
            preset.type = form.type.data
            preset.in_mode = form.in_mode.data
            preset.out_mode = form.out_mode.data
            preset.opponent_type = form.opponent.data
            preset.level = form.level.data
            preset.public_challenge = form.public_challenge.data

            db.session.commit()

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
    return render_template('game/create_X01.html', form=form, opponent_name=opponent_name,
                           title=lazy_gettext('Create Game'))


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
    game = Game.query.filter_by(hashid=hashid).first_or_404()
    # check if we found an opponent, logged in users only
    if game.status == 'challenged' and current_user.is_authenticated and current_user.id != game.player1:
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
            'game/X01_completed.html',
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
    caller = current_user.caller if current_user.is_authenticated else 'default'
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
        template = 'game/X01_stream.html'
        title = lazy_gettext('Stream overlay')
    else:
        template = 'game/X01.html'
        title = lazy_gettext('Live Match')

    return render_template(template, game=game_dict, form=form, match_json=match_json,
                            caller=caller, cpu_delay=cpu_delay, title=title,
                            chat_form=chat_form, chat_form_small=chat_form_small,
                            messages=messages, user_names=user_names,
                            settings=settings)


@bp.route('/decline_challenge/')
@bp.route('/decline_challenge/<id_>', methods=['POST'])
def decline_challenge(id_):
    id_ = int(id_)
    game = Game.query.filter_by(id=id_).first_or_404()
    game.status = "declined"
    game.end = datetime.utcnow()
    db.session.commit()
    return jsonify('success')


@bp.route('/cancel_challenge/<hashid>')
def cancel_challenge(hashid):
    game = Game.query.filter_by(hashid=hashid).first_or_404()
    game.status = "declined"
    game.end = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('generic.lobby'))


@bp.route('/abort_game/')
@bp.route('/abort_game/<hashid>', methods=['POST'])
def abort_game(hashid):
    game = Game.query.filter_by(hashid=hashid).first_or_404()
    game.status = "aborted"
    game.end = datetime.utcnow()
    broadcast_game_aborted(game)
    db.session.commit()
    return redirect(url_for('generic.lobby'))
