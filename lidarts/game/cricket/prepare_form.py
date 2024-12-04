from flask import request
from lidarts.game import bp
from lidarts.game.forms import CreateCricketGameForm
from lidarts.models import Game, CricketPresetting, UserSettings
from lidarts import db
from flask_login import current_user


def prepare_cricket_form(opponent_name, tournament_hashid):
    preset = CricketPresetting.query.filter_by(user=current_user.id).first()
    if not preset:
        preset = CricketPresetting(user=current_user.id)
        db.session.add(preset)
        db.session.commit()
    
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

    if request.args.get('wc_mode'):
        two_clear_legs_wc_mode = request.args.get('wc_mode')
    elif preset.two_clear_legs_wc_mode:
        two_clear_legs_wc_mode = preset.two_clear_legs_wc_mode
    else:
        two_clear_legs_wc_mode = False

    if request.args.get('delay'):
        score_input_delay = request.args.get('delay')
    elif preset.score_input_delay:
        score_input_delay = preset.score_input_delay
    else:
        score_input_delay = 0

    if request.args.get('webcam'):
        webcam = request.args.get('webcam')
    elif preset.webcam:
        webcam = preset.webcam
    else:
        webcam = False

    level = preset.level if preset.level else 1

    if request.args.get('opponent_name'):
        opponent_name = request.args.get('opponent_name')

    if opponent_name:
        opponent = 'online'
    else:
        opponent = preset.opponent_type if preset.opponent_type else 'online'

    public_challenge = preset.public_challenge if preset.public_challenge else False

    form = CreateCricketGameForm(
        opponent_name=opponent_name,
        opponent=opponent,
        starter=starter,
        bo_sets=bo_sets,
        bo_legs=bo_legs,
        two_clear_legs=two_clear_legs,
        two_clear_legs_wc_mode=two_clear_legs_wc_mode,
        level=level,
        public_challenge=public_challenge,
        score_input_delay=score_input_delay,
        webcam=webcam,
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

    return form