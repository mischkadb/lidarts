from lidarts import db
from lidarts.models import X01Presetting
from flask_login import current_user

def save_x01_preset(form):
    preset = X01Presetting.query.filter_by(user=current_user.id).first()
    if not preset:
        preset = X01Presetting(user=current_user.id)
        db.session.add(preset)
    preset.bo_sets = form.bo_sets.data
    preset.bo_legs = form.bo_legs.data
    preset.two_clear_legs = form.two_clear_legs.data
    preset.two_clear_legs_wc_mode = form.two_clear_legs_wc_mode.data
    preset.goal_mode = form.goal_mode.data
    preset.x_legs = form.x_legs.data
    preset.starter = form.starter.data
    preset.type = form.type.data
    preset.in_mode = form.in_mode.data
    preset.out_mode = form.out_mode.data
    preset.opponent_type = form.opponent.data
    preset.level = form.level.data
    preset.public_challenge = form.public_challenge.data
    preset.score_input_delay = form.score_input_delay.data
    preset.webcam = form.webcam.data

    db.session.commit()