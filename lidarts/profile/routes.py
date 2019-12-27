from flask import render_template, url_for, jsonify, redirect, flash, current_app, request
from flask_babelex import lazy_gettext
from flask_login import current_user, login_required
from lidarts import db, avatars
from lidarts.profile import bp
from lidarts.profile.forms import ChangeCallerForm, ChangeCPUDelayForm
from lidarts.models import User, Game, Friendship, FriendshipRequest
from sqlalchemy import desc
from datetime import datetime, timedelta
import os
import json


@bp.route('/@/<username>/game_history')
@login_required
def game_history(username):
    page = request.args.get('page', 1, type=int)

    user = User.query.filter_by(username=username).first_or_404()

    games = Game.query.filter(((Game.player1 == user.id) | (Game.player2 == user.id)) & (Game.status == 'completed')) \
        .order_by(desc(Game.id))

    games = games.paginate(page, 10, False)
    next_url = url_for('profile.game_history', username=username, page=games.next_num) \
        if games.has_next else None
    prev_url = url_for('profile.game_history', username=username, page=games.prev_num) \
        if games.has_prev else None

    player_names = {}
    for game in games.items:
        if game.player1 and game.player1 not in player_names:
            player_names[game.player1] = User.query.with_entities(User.username) \
                .filter_by(id=game.player1).first_or_404()[0]
        if game.player2 and game.player2 not in player_names:
            player_names[game.player2] = User.query.with_entities(User.username) \
                .filter_by(id=game.player2).first_or_404()[0]

    return render_template('profile/game_history.html', games=games.items, user=user, player_names=player_names,
                           next_url=next_url, prev_url=prev_url, title=lazy_gettext('Match History'))


@bp.route('/@/')
@bp.route('/@/<username>')
@login_required
def overview(username):
    player_names = {}
    user = User.query.filter(User.username.ilike(username)).first_or_404()
    games = Game.query.filter(((Game.player1 == user.id) | (Game.player2 == user.id)) & (Game.status != 'challenged')
                              & (Game.status != 'declined') & (Game.status != 'aborted')) \
        .order_by(desc(Game.id)).all()

    stats = {'darts_thrown': 0, 'double_thrown': 0, 'legs_won': 0, 'total_score': 0, 'number_of_games': 0, 'first9_scores': []}
    for game in games:
        if game.player1 and game.player1 not in player_names:
            player_names[game.player1] = User.query.with_entities(User.username) \
                .filter_by(id=game.player1).first_or_404()[0]
        if game.player2 and game.player2 not in player_names:
            player_names[game.player2] = User.query.with_entities(User.username) \
                .filter_by(id=game.player2).first_or_404()[0]

        if not (game.type == 501 and game.out_mode == 'do' and game.in_mode == 'si'):
            continue

        player = '1' if (user.id == game.player1) else '2'

        stats['number_of_games'] += 1

        match_json = json.loads(game.match_json)

        for set in match_json:
            for leg in match_json[set]:
                for score in match_json[set][leg][player]['scores'][:3]:
                    stats['first9_scores'].append(score)
                stats['darts_thrown'] += len(match_json[set][leg][player]['scores']) * 3
                stats['total_score'] += sum(match_json[set][leg][player]['scores'])
                if 'to_finish' in match_json[set][leg][player]:
                    stats['darts_thrown'] -= (3 - match_json[set][leg][player]['to_finish'])
                    stats['double_thrown'] += 1
                    stats['legs_won'] += 1
                if isinstance(match_json[set][leg][player]['double_missed'], (list,)):
                    stats['double_thrown'] += sum(match_json[set][leg][player]['double_missed'])
                else:
                    # legacy: double_missed as int
                    stats['double_thrown'] += match_json[set][leg][player]['double_missed']

    friend_query1 = Friendship.query.with_entities(Friendship.user2_id).filter_by(user1_id=current_user.id)
    friend_query2 = Friendship.query.with_entities(Friendship.user1_id).filter_by(user2_id=current_user.id)

    friend_list = friend_query1.union(friend_query2).all()
    friend_list = [r for (r,) in friend_list]

    stats['doubles'] = round((stats['legs_won'] / stats['double_thrown']), 4) * 100 if stats['double_thrown'] else 0
    stats['average'] = round((stats['total_score'] / (stats['darts_thrown'])) * 3, 2) if stats['darts_thrown'] else 0
    stats['first9_average'] = round((sum(stats['first9_scores']) / len(stats['first9_scores'])), 2) \
        if stats['first9_scores'] else 0

    avatar_url = avatars.url(user.avatar) if user.avatar else avatars.url('default.png')

    return render_template('profile/overview.html', user=user, games=games,
                           player_names=player_names, friend_list=friend_list,
                           stats=stats, avatar_url=avatar_url, title=lazy_gettext('Profile'),
                           is_online=(user.last_seen > datetime.utcnow() - timedelta(seconds=15)))


@bp.route('/set_status/')
@bp.route('/set_status/<status>', methods=['POST'])
@login_required
def set_status(status):
    user = User.query.filter_by(id=current_user.id).first_or_404()
    user.status = status
    db.session.commit()
    return jsonify('success')


@bp.route('/manage_friend_list')
@login_required
def manage_friend_list():
    player_names = {}

    friend_query1 = Friendship.query.with_entities(Friendship.user2_id).filter_by(user1_id=current_user.id)
    friend_query2 = Friendship.query.with_entities(Friendship.user1_id).filter_by(user2_id=current_user.id)

    friend_list = friend_query1.union(friend_query2).all()
    friend_list = [r for (r,) in friend_list]

    for friend in friend_list:
        if friend and friend not in player_names:
            player_names[friend] = User.query.with_entities(User.username) \
                .filter_by(id=friend).first_or_404()[0]

    friendship_request = FriendshipRequest.query.with_entities(FriendshipRequest.receiving_user_id) \
        .filter_by(requesting_user_id=current_user.id).all()

    friendship_request = [r for (r,) in friendship_request]

    for request in friendship_request:
        if request and request not in player_names:
            player_names[request] = User.query.with_entities(User.username) \
                .filter_by(id=request).first_or_404()[0]

    return render_template('profile/manage_friend_list.html',
                           friend_list=friend_list, player_names=player_names, pending_requests=friendship_request,
                           title=lazy_gettext('Manage Friend List'))


@bp.route('/delete_avatar', methods=['GET', 'POST'])
@login_required
def delete_avatar():
    if current_user.avatar:
        os.remove(os.path.join(current_app.config['UPLOADS_DEFAULT_DEST'], 'avatars', current_user.avatar))
        flash(lazy_gettext("Avatar deleted."))
    current_user.avatar = None
    db.session.commit()
    return redirect(url_for('profile.change_avatar'))


@bp.route('/change_avatar', methods=['GET', 'POST'])
@login_required
def change_avatar():
    if request.method == 'POST' and 'avatar' in request.files:
        delete_avatar()
        filename = avatars.save(request.files['avatar'], name='{}.'.format(current_user.id))
        current_user.avatar = filename
        db.session.commit()
        flash(lazy_gettext("Avatar saved."))
        return redirect(url_for('profile.change_avatar'))

    avatar_url = avatars.url(current_user.avatar) if current_user.avatar else avatars.url('default.png')

    return render_template('profile/change_avatar.html', avatar_url=avatar_url, title=lazy_gettext('Avatar Settings'))


@bp.route('/change_caller', methods=['GET', 'POST'])
@login_required
def change_caller():
    form = ChangeCallerForm(request.form)
    if form.validate_on_submit():
        current_user.caller = form.callers.data
        db.session.commit()
    form.callers.data = current_user.caller
    return render_template('profile/change_caller.html', form=form, title=lazy_gettext('Caller Settings'))


@bp.route('/change_cpu_delay', methods=['GET', 'POST'])
@login_required
def change_cpu_delay():
    form = ChangeCPUDelayForm(request.form)
    if form.validate_on_submit():
        current_user.cpu_delay = form.delay.data
        db.session.commit()
    form.delay.data = current_user.cpu_delay
    return render_template('profile/change_cpu_delay.html', form=form, title=lazy_gettext('Trainer Delay'))
