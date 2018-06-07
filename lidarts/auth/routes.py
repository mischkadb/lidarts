from flask import render_template, redirect, url_for, request, jsonify, flash
from flask_login import current_user, login_required
from lidarts import db
from lidarts.auth import bp
from lidarts.auth.forms import ChangeUsernameForm
from lidarts.models import Game, User, Chatmessage, Friendship, FriendshipRequest
from lidarts.generic.forms import ChatmessageForm
from lidarts.game.utils import get_name_by_id
from sqlalchemy import desc
from datetime import datetime, timedelta


@bp.route('/change_username', methods=['GET', 'POST'])
def change_username():
    # logged in users do not need the index page
    form = ChangeUsernameForm()
    user = User.query.filter_by(id=current_user.id).first_or_404()

    if form.validate_on_submit():
        flash('Username changed.')
        user.username = form.username.data
        db.session.commit()

    return render_template('security/change_username.html', change_username_form=form)
