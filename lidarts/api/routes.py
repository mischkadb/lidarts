from flask import jsonify
from lidarts.api import bp
from lidarts.models import Game, User
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

    game_dict = game.as_dict()
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
