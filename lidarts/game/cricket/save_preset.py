from lidarts import db
from lidarts.models import CricketPresetting
from flask_login import current_user

def save_cricket_preset(form):
    preset = CricketPresetting.query.filter_by(user=current_user.id).first()
    if not preset:
        preset = CricketPresetting(user=current_user.id)
        db.session.add(preset)
    preset.bo_sets = form.bo_sets.data
    preset.bo_legs = form.bo_legs.data
    preset.two_clear_legs = form.two_clear_legs.data
    preset.two_clear_legs_wc_mode = form.two_clear_legs_wc_mode.data
    preset.starter = form.starter.data
    preset.opponent_type = form.opponent.data
    preset.level = form.level.data
    preset.public_challenge = form.public_challenge.data
    preset.score_input_delay = form.score_input_delay.data
    preset.webcam = form.webcam.data

    db.session.commit()