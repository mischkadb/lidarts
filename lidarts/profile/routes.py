from flask import render_template, url_for, jsonify, redirect, flash, current_app, request
from flask_babelex import lazy_gettext
from flask_login import current_user, login_required
from lidarts import db, avatars, socketio
from lidarts.generic.forms import UserSearchForm
from lidarts.profile import bp
from lidarts.profile.forms import ChangeCallerForm, ChangeCPUDelayForm, GeneralSettingsForm, ChangeCountryForm, EditProfileForm, WebcamSettingsForm, LivestreamSettingsForm
from lidarts.models import Caller, User, CricketGame, Game, Friendship, FriendshipRequest, UserSettings, UserStatistic, WebcamSettings
from sqlalchemy import desc
from sqlalchemy.orm import aliased
from lidarts.utils.linker import linker
import bleach
import os
from PIL import Image
import re
import time
from datetime import datetime, timedelta
from sqlalchemy import func


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
    user = User.query.filter(func.lower(User.username)  == func.lower(username)).first()
    if not user:
        return redirect(url_for('profile.user_not_found', username=username))
    player1 = aliased(User)
    player2 = aliased(User)
    games = (
        Game.query
        .filter(
            ((Game.player1 == user.id) | (Game.player2 == user.id)) & (Game.status != 'challenged')
            & (Game.status != 'declined') & (Game.status != 'aborted')
        )
        .join(player1, Game.player1 == player1.id).add_columns(player1.username)
        .join(player2, Game.player2 == player2.id, isouter=True).add_columns(player2.username)
        .order_by(desc(Game.id)).limit(10).all()
    )

    cricket_games = (
        CricketGame.query
        .filter(
            ((CricketGame.player1 == user.id) | (CricketGame.player2 == user.id)) & (CricketGame.status != 'challenged')
            & (CricketGame.status != 'declined') & (CricketGame.status != 'aborted')
        )
        .join(player1, CricketGame.player1 == player1.id).add_columns(player1.username)
        .join(player2, CricketGame.player2 == player2.id, isouter=True).add_columns(player2.username)
        .order_by(desc(CricketGame.id)).limit(10).all()
    )
    games.extend(cricket_games)
    games.sort(key=lambda game: game[0].begin, reverse=True)

    stats = UserStatistic.query.filter_by(user=user.id).first()
    if not stats:
        stats = UserStatistic(user=user.id)
        db.session.add(stats)
        db.session.commit()

    settings = (
        UserSettings.query
        .with_entities(UserSettings.country, UserSettings.profile_text)
        .filter_by(user=user.id)
        .first()
    )

    if not settings:
        settings = UserSettings(user=user.id)
        db.session.add(settings)
        db.session.commit()
        country = None
        profile_text = None
    else:
        country, profile_text = settings


    if profile_text:
        profile_text = re.sub(
            r'(\bhttps:\/\/i\.imgur\.com\/\w+.\w+)',
            '<img src="' + r'\1' + '" style="max-width: 100%">',
            profile_text,
        )
        profile_text = linker.linkify(profile_text)
        profile_text = profile_text.replace('\n', '<br>')
        
    friend_query1 = Friendship.query.with_entities(Friendship.user2_id).filter_by(user1_id=current_user.id)
    friend_query2 = Friendship.query.with_entities(Friendship.user1_id).filter_by(user2_id=current_user.id)

    friend_list = friend_query1.union(friend_query2).all()
    friend_list = [r for (r,) in friend_list]

    avatar_url = avatars.url(f'{user.id}_thumbnail.jpg') if user.avatar else avatars.url('default.png')

    return render_template('profile/overview.html', user=user, games=games[:10],
                           player_names=player_names, friend_list=friend_list,
                           recently_online=user.recently_online(),
                           country=country, profile_text=profile_text,
                           stats=stats, avatar_url=avatar_url, title=lazy_gettext('Profile'))


@bp.route('/edit_profile/', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    user_settings = (
        UserSettings.query
        .filter_by(user=current_user.id)
        .first()
    )
    if form.validate_on_submit():
        bio_cleaned = bleach.clean(form.bio.data)
        user_settings.profile_text = bio_cleaned
        db.session.commit()
        flash(lazy_gettext('Profile text saved.'))
    if user_settings.profile_text:
        form.bio.data = user_settings.profile_text

    return render_template('profile/edit_profile.html', form=form)


@bp.route('/set_status/')
@bp.route('/set_status/<status>', methods=['POST'])
@login_required
def set_status(status):
    user = User.query.filter_by(id=current_user.id).first_or_404()
    user.status = status
    db.session.commit()
    return jsonify('success')


@bp.route('/user-not-found', methods=['POST'])
@bp.route('/user-not-found/<string:username>', methods=['GET', 'POST'])
@login_required
def user_not_found(username):
    form = UserSearchForm()
    if form.validate_on_submit():
        return redirect(url_for('profile.overview', username=form.username.data).replace('%40', '@'))
    return render_template('profile/user_not_found.html', username=username, form=form)


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
        try:
            os.remove(os.path.join(current_app.config['UPLOADS_DEFAULT_DEST'], 'avatars', current_user.avatar))
            os.remove(os.path.join(current_app.config['UPLOADS_DEFAULT_DEST'], 'avatars', f'{current_user.id}_thumbnail.jpg'))
        except:
            pass
        flash(lazy_gettext("Avatar deleted."))
    current_user.avatar = None
    db.session.commit()
    return redirect(url_for('profile.change_avatar'))


@bp.route('/change_avatar', methods=['GET', 'POST'])
@login_required
def change_avatar():
    if request.method == 'POST' and 'avatar' in request.files:
        avatar_file = request.files['avatar']
        if avatar_file.filename == '':
            flash(lazy_gettext('No selected file'), 'danger')
            return redirect(request.url)
        delete_avatar()
        filename = avatars.save(avatar_file, name='{}.'.format(current_user.id))
        image = os.path.join(current_app.config['UPLOADS_DEFAULT_DEST'], 'avatars', filename)
        if image.split('.')[-1].lower() not in ['jpg', 'jpeg', 'gif', 'png']:
            flash(lazy_gettext('Wrong image format.'))
            return redirect(url_for('profile.change_avatar'))
        im = Image.open(image)
        rgb_im = im.convert('RGB')
        rgb_im.thumbnail((64, 64), Image.BICUBIC)
        rgb_im.save(os.path.join(current_app.config['UPLOADS_DEFAULT_DEST'], 'avatars', f'{current_user.id}_thumbnail.jpg'), "JPEG")
        current_user.avatar = filename
        current_user.avatar_version = int(time.time())
        db.session.commit()
        flash(lazy_gettext("Avatar saved."))
        return redirect(url_for('profile.change_avatar'))

    avatar_url = avatars.url(current_user.avatar) if current_user.avatar else avatars.url('default.png')

    return render_template('profile/change_avatar.html', avatar_url=avatar_url, title=lazy_gettext('Avatar Settings'))


@bp.route('/change_caller', methods=['GET', 'POST'])
@login_required
def change_caller():
    callers = Caller.query.all()
    caller_list = []
    for caller in callers:
        caller_list.append((caller.name, caller.display_name))
    form = ChangeCallerForm(request.form)
    form.callers.choices = caller_list
    settings = UserSettings.query.filter_by(user=current_user.id).first()
    if not settings:
        settings = UserSettings(user=current_user.id)
        db.session.add(settings)
        db.session.commit()

    if form.validate_on_submit():        
        settings.caller = form.callers.data
        db.session.commit()
        flash(lazy_gettext('Settings saved.'))
    form.callers.data = settings.caller
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


@bp.route('/general_settings', methods=['GET', 'POST'])
@login_required
def general_settings():
    form = GeneralSettingsForm()
    country_form = ChangeCountryForm()
    settings = UserSettings.query.filter_by(user=current_user.id).first()

    if form.validate_on_submit():
        settings.notification_sound = True if form.notification_sound.data == 'enabled' else False
        settings.allow_challenges = True if form.allow_challenges.data == 'enabled' else False
        settings.allow_private_messages = True if form.allow_private_messages.data == 'enabled' else False
        settings.allow_friend_requests = True if form.allow_friend_requests.data == 'enabled' else False
        settings.checkout_suggestions = True if form.checkout_suggestions.data == 'enabled' else False
        settings.show_average_in_chat_list = True if form.show_average_in_chat_list.data == 'enabled' else False
        db.session.commit()
        flash(lazy_gettext("Settings saved."))

    if country_form.validate_on_submit():
        if settings.country != country_form.country.data:
            country_changed_recently = settings.last_country_change and settings.last_country_change > datetime.utcnow() - timedelta(days=30)
            if settings.country and country_changed_recently:
                cooldown_timestamp = (settings.last_country_change + timedelta(days=30)).strftime('%d.%m.%Y, %H:%M:%S')
                flash(lazy_gettext('You can only change your country setting once per month. You need to wait until: ') + cooldown_timestamp + ' UTC.', 'danger')
                return render_template('profile/general_settings.html', form=form, country_form=country_form, title=lazy_gettext('General settings'))

            settings.country = country_form.country.data if country_form.country.data and country_form.country.data != 'None' else None
            settings.last_country_change = datetime.utcnow()
        db.session.commit()
        flash(lazy_gettext("Settings saved."))


    form.notification_sound.data = 'enabled' if settings.notification_sound else 'disabled'
    form.allow_challenges.data = 'enabled' if settings.allow_challenges else 'disabled'
    form.allow_private_messages.data = 'enabled' if settings.allow_private_messages else 'disabled'
    form.allow_friend_requests.data = 'enabled' if settings.allow_friend_requests else 'disabled'
    form.checkout_suggestions.data = 'enabled' if settings.checkout_suggestions else 'disabled'
    form.show_average_in_chat_list.data = 'enabled' if settings.show_average_in_chat_list else 'disabled'    
    country_form.country.data = settings.country if settings.country else None
    
    return render_template('profile/general_settings.html', form=form, country_form=country_form, title=lazy_gettext('General settings'))


@bp.route('/webcam_settings', methods=['GET', 'POST'])
@login_required
def webcam_settings():
    form = WebcamSettingsForm()
    settings = WebcamSettings.query.filter_by(user=current_user.id).first()

    if form.validate_on_submit():
        settings.activated = True if form.activated.data == 'enabled' else False
        settings.stream_consent = True if form.stream_consent.data == 'enabled' else False
        settings.mobile_app = True if form.mobile_app.data == 'enabled' else False
        settings.mobile_follower_mode = True if form.mobile_follower_mode.data == 'enabled' else False
        settings.force_scoreboard_page = True if form.force_scoreboard_page.data == 'enabled' else False
        db.session.commit()
        flash(lazy_gettext("Settings saved."))

    form.activated.data = 'enabled' if settings.activated else 'disabled'
    form.stream_consent.data = 'enabled' if settings.stream_consent else 'disabled'
    form.mobile_app.data = 'enabled' if settings.mobile_app else 'disabled'
    form.mobile_follower_mode.data = 'enabled' if settings.mobile_follower_mode else 'disabled'
    form.force_scoreboard_page.data = 'enabled' if settings.force_scoreboard_page else 'disabled'
    
    return render_template('profile/webcam_settings.html', form=form, title=lazy_gettext('Webcam settings'))


@bp.route('/livestream_settings', methods=['GET', 'POST'])
@login_required
def livestream_settings():
    form = LivestreamSettingsForm()
    settings = UserSettings.query.filter_by(user=current_user.id).first()

    if form.validate_on_submit():
        settings.channel_id = form.channel_id.data
        db.session.commit()
        flash(lazy_gettext("Settings saved."))

    form.channel_id.data = settings.channel_id
    
    return render_template('profile/livestream_settings.html', form=form, title=lazy_gettext('Livestream settings'))
