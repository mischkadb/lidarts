from flask import jsonify
from lidarts.api import bp
from lidarts.models import Game
from lidarts.game.utils import collect_statistics
import json


@bp.route('/game/<hashid>')
def start(hashid):
    game = (
        Game.query
        .filter_by(hashid=hashid)
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

    return jsonify(return_dict)
