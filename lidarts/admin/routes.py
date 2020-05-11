from flask import jsonify, current_app, flash, render_template
from flask_babelex import lazy_gettext
from flask_login import current_user, login_required
from lidarts import db
from lidarts.admin import bp
from lidarts.models import Game, CricketGame, User, StreamGame, WebcamSettings, GameBaseNew, CricketGameNew, X01Game
from lidarts.tournament.forms import ConfirmStreamGameForm
from sqlalchemy import desc


@bp.route('/<api_key>/game/stream-games', methods=['GET', 'POST'])
@bp.route('/<api_key>/game/stream-games/<tournament_hashid>', methods=['GET', 'POST'])
@login_required
def streamable_games(api_key, tournament_hashid=None):
    form = ConfirmStreamGameForm()
    if api_key != current_app.config['API_KEY']:
        return jsonify('Wrong API key.')

    games_query = Game.query

    if tournament_hashid:
        games_query = games_query.filter_by(tournament=tournament_hashid)

    games = (
        games_query
        .filter_by(webcam=True)
        .filter_by(status='started')
        .order_by(Game.id.desc())
        .limit(30)
        .all()
    )

    streamable_games = {}
    user_names = {}
    choices = []

    for game in games:
        player1 = WebcamSettings.query.filter_by(user=game.player1).first()
        if not player1.stream_consent:
            continue
        player2 = WebcamSettings.query.filter_by(user=game.player2).first()
        if not player2.stream_consent:
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
        'admin/stream.html',
        games=streamable_games,
        user_names=user_names,
        form=form,
        title=lazy_gettext('Streaming'),
    )


@bp.route('/<api_key>/add_x01')
@login_required
def add_x01(api_key):
    if api_key != current_app.config['API_KEY']:
        return jsonify('Wrong API key.')

    games = Game.query.all()
    cricket_games = CricketGame.query.all()
    games.extend(cricket_games)
    games.sort(key=lambda k: k.begin)
    for game in games:
        base_game = GameBaseNew.query.filter_by(hashid=game.hashid).first()
        if base_game:
            continue
        if isinstance(game, Game):
            base_game = X01Game()
            base_game.variant = 'x01'
            base_game.type = game.type
            base_game.in_mode = game.in_mode
            base_game.out_mode = game.out_mode
        else:
            base_game = CricketGameNew()
            base_game.variant = 'cricket'
            base_game.confirmation_needed = game.confirmation_needed
            base_game.undo_possible = game.undo_possible
        base_game.hashid = game.hashid
        base_game.bo_sets = game.bo_sets
        base_game.bo_legs = game.bo_legs
        base_game.two_clear_legs = game.two_clear_legs
        base_game.p1_sets = game.p1_sets
        base_game.p2_sets = game.p2_sets
        base_game.p1_legs = game.p1_legs
        base_game.p2_legs = game.p2_legs
        base_game.p1_score = game.p1_score
        base_game.p2_score = game.p2_score
        base_game.p1_next_turn = game.p1_next_turn
        base_game.closest_to_bull = game.closest_to_bull
        base_game.closest_to_bull_json = game. closest_to_bull_json
        base_game.status = game.status
        base_game.match_json = game.match_json
        base_game.begin = game.begin
        base_game.end = game.end
        base_game.opponent_type = game.opponent_type
        base_game.public_challenge = game.public_challenge
        base_game.score_input_delay = game.score_input_delay
        base_game.webcam = game.webcam
        base_game.jitsi_hashid = game.jitsi_hashid
        base_game.tournament_stage_game_id = game.tournament_stage_game_id
        base_game.tournament_stage_game_bracket_id = game.tournament_stage_game_bracket_id
        base_game.tournament = game.tournament
        base_game.player1 = game.player1
        base_game.player2 = game.player2
        db.session.add(base_game)
        print(game, game.bo_sets)
    db.session.commit()

    return jsonify('success')