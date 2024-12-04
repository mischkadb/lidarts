from flask import jsonify, current_app, redirect, url_for
from flask_login import current_user, login_required
from lidarts import db
from lidarts.api import bp
from lidarts.models import Game, CricketGame, User, StreamGame, Tournament
from lidarts.game.utils import collect_statistics
import json
from sqlalchemy.orm import aliased


@bp.route('/game/<hashid>')
def start(hashid):
    player1 = aliased(User)
    player2 = aliased(User)
    game, p1_name, p2_name = (
        Game.query
        .join()
        .filter_by(hashid=hashid)
        .join(player1, Game.player1 == player1.id).add_columns(player1.username)
        .join(player2, Game.player2 == player2.id, isouter=True).add_columns(player2.username)
        .first_or_404()
    )

    match_json = json.loads(game.match_json)
    statistics = collect_statistics(game, match_json)

    game_dict = game.__dict__
    keys = (
        'begin',
        'end',
        'bo_legs',
        'bo_sets',
        'hashid',
        'match_json',
        'p1_legs',
        'p2_legs',
        'p1_sets',
        'p2_sets',
        'player1',
        'player2',
        'type',
        'two_clear_legs',
        'two_clear_legs_wc_mode',
        'status',
        'in_mode',
        'out_mode',
    )

    return_dict = {}
    for key in keys:
        return_dict[key] = game_dict[key]

    for stat_key, stat in statistics.items():
        return_dict[stat_key] = stat

    return_dict['p1_name'] = p1_name
    return_dict['p2_name'] = p2_name

    return jsonify(return_dict)


@bp.route('/<api_key>/game/stream-game/<hashid>')
def set_stream_game(api_key, hashid):
    game = Game.query.filter_by(hashid=hashid).first()
    if not game:
        game = CricketGame.query.filter_by(hashid=hashid).first_or_404()

    if api_key != current_app.config['API_KEY']:
        if not game.tournament:
            return jsonify('Not a tournament game.')

        tournament = Tournament.query.filter_by(hashid=game.tournament).first()
        if not tournament.api_key:
            return jsonify('Tournament API key not set.')

        if tournament.creator != current_user.id:
            return jsonify('Not your tournament.')

    if api_key != current_app.config['API_KEY'] and api_key != tournament.api_key:
        return jsonify('Wrong API key.')

    stream_game = StreamGame.query.filter_by(user=current_user.id).first()
    if not stream_game:
        stream_game = StreamGame(user=current_user.id)
        db.session.add(stream_game)
    stream_game.hashid = hashid
    stream_game.jitsi_hashid = game.jitsi_hashid    
    db.session.commit()

    return hashid


@bp.route('/game/stream-game')
@login_required
def get_stream_game():
    stream_game = StreamGame.query.filter_by(user=current_user.id).first_or_404()
    hashid = stream_game.hashid

    return redirect(url_for('game.start', hashid=hashid, theme='streamoverlay'))


@bp.route('/game/stream-game/jitsi')
@login_required
def get_jitsi():
    stream_game = StreamGame.query.filter_by(user=current_user.id).first_or_404()
    game = Game.query.filter_by(hashid=stream_game.hashid).first_or_404()
    jitsi_server = 'meet.jit.si' if game.jitsi_public_server else 'jitsi.dusk-server.de'
    hashid = stream_game.jitsi_hashid    

    return redirect(f'https://{jitsi_server}/lidarts-{hashid}', code=302)
