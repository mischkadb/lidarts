from flask import render_template, redirect, url_for, jsonify, request
from lidarts.game import bp
from lidarts.game.forms import CreateX01GameForm, ScoreForm
from lidarts.models import Game
from lidarts import db
from lidarts.socket.chat_handler import broadcast_new_game
from lidarts.game.utils import get_name_by_id, collect_statistics
from lidarts.socket.X01_game_handler import start_game
from flask_login import current_user, login_required
from datetime import datetime
import json


@bp.route('/create', methods=['GET', 'POST'])
@bp.route('/create/<mode>', methods=['GET', 'POST'])
@login_required
def create(mode='x01'):
    if mode == 'x01':
        form = CreateX01GameForm()
    else:
        pass  # no other game modes yet
    if form.validate_on_submit():
        player1 = current_user.id if current_user.is_authenticated else None
        if player1 and form.opponent.data == 'local':
            player2 = current_user.id
            status = 'started'
        elif player1 and form.opponent.data == 'online':
            player2 = None
            status = 'challenged'
        else:
            # computer as opponent
            player2 = None
            status = 'started'
        match_json = json.dumps({1: {1: {1: [], 2: []}}})
        game = Game(player1=player1, player2=player2, type=form.type.data,
                    bo_sets=form.bo_sets.data, bo_legs=form.bo_legs.data,
                    p1_sets=0, p2_sets=0, p1_legs=0, p2_legs=0,
                    p1_score=int(form.type.data), p2_score=int(form.type.data),
                    in_mode=form.in_mode.data, out_mode=form.out_mode.data,
                    begin=datetime.now(), match_json=match_json,
                    status=status, opponent_type=form.opponent.data)
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
    return render_template('game/create_X01.html', form=form)


@bp.route('/')
@bp.route('/<hashid>')
@bp.route('/<hashid>/<theme>')
def start(hashid, theme=None):
    game = Game.query.filter_by(hashid=hashid).first_or_404()
    # check if we found an opponent, logged in users only
    if game.status == 'challenged' and current_user.is_authenticated \
            and current_user.id != game.player1 and not game.player2:
        game.player2 = current_user.id
        game.status = 'started'
        db.session.commit()
        # send message to global chat
        if not game.opponent_type.startswith('computer'):
            broadcast_new_game(game)
        # signal the waiting player and spectators
        start_game(hashid)

    game_dict = game.as_dict()
    if game.player1:
        game_dict['player1_name'] = get_name_by_id(game.player1)

    if game.opponent_type == 'local':
        game_dict['player2_name'] = 'Local Guest'
    elif game.opponent_type == 'online':
        game_dict['player2_name'] = get_name_by_id(game.player2)
    else:
        # computer game
        game_dict['player2_name'] = 'Trainer'

    match_json = json.loads(game.match_json)

    # for player1 and spectators while waiting
    if game.status == 'challenged':
        return render_template('game/wait_for_opponent.html', game=game_dict)
    # for everyone if the game is completed
    if game.status == 'completed':
        statistics = collect_statistics(game, match_json)
        return render_template('game/X01_completed.html', game=game_dict, match_json=match_json, stats=statistics)
    # for running games
    else:
        form = ScoreForm()
        if theme:
            return render_template('game/X01_stream.html', game=game_dict, form=form, match_json=match_json)
        return render_template('game/X01.html', game=game_dict, form=form, match_json=match_json)


@bp.route('/validate_score', methods=['POST'])
def validate_score():
    # validating the score input from users
    form = ScoreForm(request.form)
    result = form.validate()
    return jsonify(form.errors)
