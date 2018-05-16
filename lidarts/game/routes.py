from flask import render_template, redirect, url_for
from flask_login import current_user
from lidarts.game import bp
from lidarts.game.forms import CreateX01GameForm


@bp.route('/create', methods=['GET', 'POST'])
@bp.route('/create/<mode>', methods=['GET', 'POST'])
def create(mode='x01'):
    if mode == 'x01':
        form = CreateX01GameForm()
    else:
        pass
    return render_template('game/create_X01.html', form=form)
