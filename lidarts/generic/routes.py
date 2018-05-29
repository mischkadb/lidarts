from flask import render_template, redirect, url_for
from flask_login import current_user, login_required
from lidarts import db
from lidarts.generic import bp
from lidarts.models import Game, User, Chatmessage
from lidarts.generic.forms import ChatmessageForm
from sqlalchemy import desc
from datetime import datetime, timedelta


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/')
def index():
    # logged in users do not need the index page
    if current_user.is_authenticated:
        return redirect(url_for('generic.lobby'))
    return render_template('generic/index.html')


@bp.route('/about')
def about():
    return render_template('generic/index.html')


@bp.route('/lobby')
@login_required
def lobby():
    player_names = {}
    games_in_progress = Game.query.filter(((Game.player1 == current_user.id) | (Game.player2 == current_user.id)) & \
                                          (Game.status == 'started')).order_by(desc(Game.id)).all()
    for game in games_in_progress:
        if game.player1 and game.player1 not in player_names:
            player_names[game.player1] = User.query.with_entities(User.username)\
                .filter_by(id=game.player1).first_or_404()[0]
        if game.player2 and game.player2 not in player_names:
            player_names[game.player2] = User.query.with_entities(User.username) \
                .filter_by(id=game.player2).first_or_404()[0]

    return render_template('generic/lobby.html', games_in_progress=games_in_progress, player_names=player_names)


@bp.route('/chat')
@login_required
def chat():
    form = ChatmessageForm()
    messages = Chatmessage.query.filter(Chatmessage.timestamp > (datetime.now() - timedelta(days=1))).all()
    user_names = {}

    for message in messages:
        user_names[message.author] = User.query.with_entities(User.username)\
                .filter_by(id=message.author).first_or_404()[0]

    return render_template('generic/chat.html', form=form, messages=messages, user_names=user_names)


