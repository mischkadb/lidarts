from flask import render_template
from lidarts.profile import bp
from lidarts.models import User, Game
from sqlalchemy import desc


@bp.route('/@/<username>')
def overview(username):
    user = User.query.filter_by(username=username).first_or_404()
    games = Game.query.filter((Game.player1 == user.id) | (Game.player2 == user.id)).order_by(desc(Game.id)).all()
    return render_template('profile/overview.html', user=user, games=games)
