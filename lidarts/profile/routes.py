from flask import render_template
from flask_login import current_user
from lidarts.profile import bp
from lidarts.models import User, Game, Friendship, FriendshipRequest
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
                           is_online=(user.last_seen > datetime.now() - timedelta(minutes=5)))


@bp.route('/manage_friend_list')
def manage_friend_list():
    player_names = {}

    friend_query1 = Friendship.query.with_entities(Friendship.user2_id).filter_by(user1_id=current_user.id)
    friend_query2 = Friendship.query.with_entities(Friendship.user1_id).filter_by(user2_id=current_user.id)

    friend_list = friend_query1.union(friend_query2).all()
    friend_list = [r for (r,) in friend_list]

    for friend in friend_list:
        if friend and friend not in player_names:
            player_names[friend] = User.query.with_entities(User.username)\
                .filter_by(id=friend).first_or_404()[0]

    friendship_request = FriendshipRequest.query.with_entities(FriendshipRequest.receiving_user_id)\
        .filter_by(requesting_user_id=current_user.id).all()

    friendship_request = [r for (r, ) in friendship_request]

    for request in friendship_request:
        if request and request not in player_names:
            player_names[request] = User.query.with_entities(User.username)\
                .filter_by(id=request).first_or_404()[0]

    return render_template('profile/manage_friend_list.html',
                           friend_list=friend_list, player_names=player_names, pending_requests=friendship_request)
