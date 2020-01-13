from flask import render_template, redirect, url_for, request, jsonify
from flask_babelex import lazy_gettext
from flask_login import current_user, login_required
from lidarts import db
from lidarts.generic import bp
from lidarts.models import Game, User, Chatmessage, Friendship, FriendshipRequest, Privatemessage, Notification
from lidarts.generic.forms import ChatmessageForm
from lidarts.game.forms import GameChatmessageForm
from lidarts.profile.utils import get_user_status
from lidarts.socket.utils import broadcast_online_players
from sqlalchemy import desc
from datetime import datetime, timedelta
from collections import defaultdict


@bp.route('/')
def index():
    # logged in users do not need the index page
    if current_user.is_authenticated:
        return redirect(url_for('generic.lobby'))
    return render_template('generic/index.html')


@bp.route('/about')
def about():
    return render_template('generic/about.html')


@bp.route('/contact')
def contact():
    return render_template('generic/contact.html')


@bp.route('/changelog')
def changelog():
    return render_template('generic/changelog.html')


@bp.route('/contribute')
def contribute():
    return render_template('generic/contribute.html')


@bp.route('/watch')
def live_games_overview():
    live_games = Game.query.filter((Game.status == 'started')).order_by(Game.begin.desc())
    live_games_list = []
    players_in_list = []

    for game in live_games:
        game_dict = game.as_dict()
        player1_active = True
        player2_active = True
        player1_in_player_list = False
        player2_in_player_list = False

        if game.player1:
            player1 = User.query.get(game.player1)
            game_dict['player1_name'] = player1.username
            player1_active = player1.last_seen_ingame > datetime.utcnow() - timedelta(minutes=5)
            player1_in_player_list = game.player1 in players_in_list
        if game.player2:
            player2 = User.query.get(game.player2)
            # Local Guest needs his own 'name'
            game_dict['player2_name'] = player2.username if game.player1 != game.player2 else lazy_gettext('Local Guest')
            player2_active = player2.last_seen_ingame > datetime.utcnow() - timedelta(minutes=5)
            player2_in_player_list = game.player2 in players_in_list

        # only show game in watch tab if both players are recently ingame
        if player1_active and player2_active and not player1_in_player_list and not player2_in_player_list:
            live_games_list.append(game_dict)
            if game.player1:
                players_in_list.append(game.player1)
            if game.player2:
                players_in_list.append(game.player2)

        if len(live_games_list) >= 9:
            break

    return render_template('generic/watch.html', live_games=live_games_list, title=lazy_gettext('Live Games'))


@bp.route('/lobby')
@login_required
def lobby():
    player_names = {}
    games_in_progress = Game.query.filter(((Game.player1 == current_user.id) | (Game.player2 == current_user.id)) & \
                                          (Game.status == 'started')).order_by(desc(Game.id)).all()
    for game in games_in_progress:
        if game.player1 and game.player1 not in player_names:
            player_names[game.player1] = User.query.with_entities(User.username) \
                .filter_by(id=game.player1).first_or_404()[0]
        if game.player2 and game.player2 not in player_names:
            player_names[game.player2] = User.query.with_entities(User.username) \
                .filter_by(id=game.player2).first_or_404()[0]

    # get challenges
    challenges = Game.query.filter_by(status='challenged', player2=current_user.id).all()
    for game in challenges:
        player_names[game.player1] = User.query.with_entities(User.username) \
            .filter_by(id=game.player1).first_or_404()[0]
    challenges = [r.as_dict() for r in challenges]

    # get friend requests
    friend_requests = FriendshipRequest.query.filter_by(receiving_user_id=current_user.id).all()
    for friend_request in friend_requests:
        if friend_request.requesting_user_id not in player_names:
            player_names[friend_request.requesting_user_id] = User.query.with_entities(User.username) \
                .filter_by(id=friend_request.requesting_user_id).first_or_404()[0]

    # get online friends
    friend_query1 = Friendship.query.with_entities(Friendship.user2_id).filter_by(user1_id=current_user.id)
    friend_query2 = Friendship.query.with_entities(Friendship.user1_id).filter_by(user2_id=current_user.id)
    online_users = User.query.with_entities(User.id).filter(User.last_seen > datetime.utcnow() - timedelta(seconds=15))

    online_friend_list = friend_query1.union(friend_query2).intersect(online_users).all()
    online_friend_list = [r for r, in online_friend_list]

    for friend in online_friend_list:
        if friend not in player_names:
            player_names[friend] = User.query.with_entities(User.username) \
                .filter_by(id=friend).first_or_404()[0]

    return render_template('generic/lobby.html', games_in_progress=games_in_progress, player_names=player_names,
                           friend_requests=friend_requests, online_friend_list=online_friend_list,
                           challenges=challenges, title=lazy_gettext('Lobby'))


@bp.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    form = ChatmessageForm()
    messages = Chatmessage.query.filter(Chatmessage.timestamp > (datetime.utcnow() - timedelta(days=1))) \
        .order_by(Chatmessage.id.asc()).all()
    user_names = {}

    for message in messages:
        user_names[message.author] = User.query.with_entities(User.username) \
            .filter_by(id=message.author).first_or_404()[0]

    return render_template('generic/chat.html', form=form, messages=messages,
                           user_names=user_names, title=lazy_gettext('Chat'))


# should get called by a cronjob periodically
@bp.route('/chat/broadcast_online_players')
def chat_broadcast_online_players_periodic():
    broadcast_online_players()
    return jsonify('success')


# should get called by a cronjob periodically
@bp.route('/abort_long_started_games')
def abort_long_started_games():
    games = Game.query.filter((Game.status == 'started') & (Game.begin < (datetime.utcnow() - timedelta(days=3)))).all()
    for game in games:
        game.status = 'aborted'
        game.end = datetime.utcnow()
    db.session.commit()
    return jsonify('success')


@bp.route('/get_id_by_username/')
@bp.route('/get_id_by_username/<username>')
def get_id_by_username(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify('error')
    return jsonify(user.id)


@bp.route('/private_messages', methods=['GET', 'POST'])
@login_required
def private_messages():
    form = ChatmessageForm()
    messages_sent = Privatemessage.query.filter_by(sender=current_user.id)
    messages_received = Privatemessage.query.filter_by(receiver=current_user.id)
    messages = messages_sent.union(messages_received).order_by(Privatemessage.id.asc()).all()
    user_names = {current_user.id: current_user.username}
    messages_dict = defaultdict(list)
    status = {}

    for message in messages:
        other_user = message.sender if message.sender != current_user.id else message.receiver
        messages_dict[other_user].append({'sender': message.sender, 'receiver': message.receiver,
                                          'message': message.message, 'timestamp': message.timestamp})

        if other_user not in user_names:
            other_user = User.query.filter_by(id=other_user).first_or_404()
            user_names[other_user.id] = other_user.username
            status[other_user.id] = get_user_status(other_user)

    return render_template('generic/inbox.html', form=form, messages=messages_dict,
                           user_names=user_names, status=status, title=lazy_gettext('Private Messages'))


@bp.route('/compose_message/')
@bp.route('/compose_message/<name>', methods=['POST'])
@login_required
def compose_message(name=None):
    user = User.query.filter_by(username=name).first()
    if not user or user == current_user:
        return jsonify('error')
    user_dict = dict(
        id=user.id, username=user.username, status=user.status, avatar=user.avatar
    )
    return jsonify(user_dict)


@bp.route('/validate_game_chat_message', methods=['POST'])
@login_required
def validate_game_chat_message():
    # validating the score input from users
    form = GameChatmessageForm(request.form)
    result = form.validate()
    return jsonify(form.errors)


@bp.route('/validate_chat_message', methods=['POST'])
@login_required
def validate_chat_message():
    # validating the score input from users
    form = ChatmessageForm(request.form)
    result = form.validate()
    return jsonify(form.errors)


@bp.route('/send_friend_request/')
@bp.route('/send_friend_request/<id>', methods=['POST'])
@login_required
def send_friend_request(id):
    id = int(id)
    if current_user.id == id:
        return 'error'
    friendship = Friendship.query \
        .filter(((Friendship.user1_id == id) & (Friendship.user2_id == current_user.id))
                | ((Friendship.user2_id == id) & (Friendship.user1_id == current_user.id))).first()

    if not friendship:
        friendship_request = FriendshipRequest.query \
            .filter(((FriendshipRequest.requesting_user_id == id)
                     & (FriendshipRequest.receiving_user_id == current_user.id))
                    | ((FriendshipRequest.receiving_user_id == id)
                       & (FriendshipRequest.requesting_user_id == current_user.id))).first()

        if not friendship_request:
            friendship_request = FriendshipRequest(requesting_user_id=current_user.id, receiving_user_id=id)
            db.session.add(friendship_request)
            db.session.commit()
    return jsonify('success')


@bp.route('/accept_friend_request/')
@bp.route('/accept_friend_request/<id>', methods=['POST'])
@login_required
def accept_friend_request(id):
    id = int(id)
    friendship_request = FriendshipRequest.query \
        .filter(((FriendshipRequest.requesting_user_id == id) &
                 (FriendshipRequest.receiving_user_id == current_user.id))
                | ((FriendshipRequest.receiving_user_id == id) &
                   (FriendshipRequest.requesting_user_id == current_user.id))).all()

    if friendship_request:
        friendship = Friendship(user1_id=friendship_request[0].requesting_user_id,
                                user2_id=friendship_request[0].receiving_user_id)
        db.session.add(friendship)

        for request in friendship_request:
            db.session.delete(request)

        db.session.commit()
        return jsonify('success')

    return jsonify('failure')


@bp.route('/decline_friend_request/')
@bp.route('/decline_friend_request/<id>', methods=['POST'])
@login_required
def decline_friend_request(id):
    id = int(id)
    friendship_request = FriendshipRequest.query \
        .filter(((FriendshipRequest.requesting_user_id == id) &
                 (FriendshipRequest.receiving_user_id == current_user.id))
                | ((FriendshipRequest.receiving_user_id == id) &
                   (FriendshipRequest.requesting_user_id == current_user.id))).all()

    if friendship_request:
        for request in friendship_request:
            db.session.delete(request)

        db.session.commit()
        return jsonify('success')

    return jsonify('failure')


@bp.route('/remove_friend/')
@bp.route('/remove_friend/<id>', methods=['POST'])
@login_required
def remove_friend(id):
    id = int(id)
    friendship = Friendship.query \
        .filter(((Friendship.user1_id == id) &
                 (Friendship.user2_id == current_user.id))
                | ((Friendship.user2_id == id) &
                   (Friendship.user1_id == current_user.id))).first()

    if friendship:
        db.session.delete(friendship)

        db.session.commit()
        return jsonify('success')

    return jsonify('failure')


@bp.route('/remove_friend_request/')
@bp.route('/remove_friend_request/<id>', methods=['POST'])
@login_required
def remove_friend_request(id):
    id = int(id)
    friendship_request = FriendshipRequest.query \
        .filter(((FriendshipRequest.requesting_user_id == current_user.id) &
                 (FriendshipRequest.receiving_user_id == id))).first()

    if friendship_request:
        db.session.delete(friendship_request)

        db.session.commit()
        return jsonify('success')

    return jsonify('failure')


@bp.route('/notifications_read', methods=['POST'])
@login_required
def notifications_read():
    notifications = Notification.query.filter_by(user=current_user.id).all()
    for notification in notifications:
        db.session.delete(notification)
    db.session.commit()
    return jsonify('success')

