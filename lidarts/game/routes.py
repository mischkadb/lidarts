from flask import render_template, redirect, url_for, jsonify, request
from lidarts.game import bp
from lidarts.game.forms import CreateX01GameForm, ScoreForm
from lidarts.models import Game
from lidarts import db
from lidarts.game.utils import get_name_by_id
from lidarts.socket.X01_game_handler import start_game
from flask_login import current_user
from datetime import datetime
import json


@bp.route('/create', methods=['GET', 'POST'])
@bp.route('/create/<mode>', methods=['GET', 'POST'])
def create(mode='x01'):
    if mode == 'x01':
        form = CreateX01GameForm()
    else:
        pass  # no other game modes yet
    if form.validate_on_submit():
        player1 = current_user.id if current_user.is_authenticated else None
        if current_user.is_authenticated and form.opponent.data == 'local':
            player2 = current_user.id
            status = 'started'
        else:
            player2 = None
            status = 'challenged'
        match_json = json.dumps({1: {1: {1: [], 2: []}}})
        game = Game(player1=player1, player2=player2, type=form.type.data,
                    bo_sets=form.bo_sets.data, bo_legs=form.bo_legs.data,
                    p1_sets=0, p2_sets=0, p1_legs=0, p2_legs=0,
                    p1_score=int(form.type.data), p2_score=int(form.type.data),
                    in_mode=form.in_mode.data, out_mode=form.out_mode.data,
                    begin=datetime.now(), match_json=match_json, status=status)
        game.p1_next_turn = form.starter.data == 'me'
        db.session.add(game)
        db.session.commit()  # needed to get a game id for the hashid
        game.set_hashid()
        db.session.commit()
        return redirect(url_for('game.start', hashid=game.hashid))
    return render_template('game/create_X01.html', form=form)


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
        # signal the waiting player and spectators
        start_game(hashid)

    game_dict = game.as_dict()
    if game.player1:
        game_dict['player1_name'] = get_name_by_id(game.player1)
    if game.player2:
        # Local Guest needs his own 'name'
        game_dict['player2_name'] = get_name_by_id(game.player2) if game.player1 != game.player2 else 'Local Guest'
    match_json = json.loads(game.match_json)

    # for player1 and spectators while waiting
    if game.status == 'challenged':
        return render_template('game/wait.html', game=game_dict)
    # for everyone if the game is completed
    if game.status == 'completed':
        return render_template('game/X01_completed.html', game=game_dict, match_json=match_json)
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
