from flask import jsonify, current_app, flash, render_template
from flask_babelex import lazy_gettext
from flask_login import current_user, login_required
from lidarts import db
from lidarts.admin import bp
from lidarts.models import Game, CricketGame, User, StreamGame, WebcamSettings
from lidarts.tournament.forms import ConfirmStreamGameForm
from sqlalchemy import desc


@bp.route('/admin/panel', methods=['GET'])
def admin_panel():
    pass


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
        'admin/stream.html',
        games=streamable_games,
        user_names=user_names,
        form=form,
        title=lazy_gettext('Streaming'),
    )
