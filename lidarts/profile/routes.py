from flask import render_template
from lidarts.profile import bp
from lidarts.models import User, Game
from sqlalchemy import desc
from datetime import datetime, timedelta

@bp.route('/@/')
@bp.route('/@/<username>')
def overview(username):
    player_names = {}
    user = User.query.filter(User.username.ilike(username)).first_or_404()
    games = Game.query.filter((Game.player1 == user.id) | (Game.player2 == user.id) & (Game.status != 'challenged'))\
        .order_by(desc(Game.id)).all()

    for game in games:
        if game.player1 and game.player1 not in player_names:
            player_names[game.player1] = User.query.with_entities(User.username)\
                .filter_by(id=game.player1).first_or_404()[0]
        if game.player2 and game.player2 not in player_names:
            player_names[game.player2] = User.query.with_entities(User.username) \
                .filter_by(id=game.player2).first_or_404()[0]


    return render_template('profile/overview.html', user=user, games=games,
                           player_names=player_names,
                           is_online=(user.last_seen > datetime.now()- timedelta(minutes=5)))
