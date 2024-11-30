from flask import render_template, flash
from flask_login import current_user, login_required
from flask_babelex import lazy_gettext
from lidarts import db
from lidarts.auth import bp
from lidarts.auth.forms import ChangeUsernameForm
from lidarts.models import User, UsernameChange
from datetime import datetime, timedelta


@bp.route('/change_username', methods=['GET', 'POST'])
@login_required
def change_username():
    # logged in users do not need the index page
    form = ChangeUsernameForm()
    user = User.query.filter_by(id=current_user.id).first_or_404()

    if form.validate_on_submit():        
        if user.username == form.username.data:
            return render_template('security/change_username.html', change_username_form=form, title=lazy_gettext('Change username'))
        
        last_change = (
            UsernameChange.query
            .filter_by(user=current_user.id)
            .order_by(UsernameChange.timestamp.desc())
            .first()
        )
        
        if last_change and last_change.timestamp > datetime.utcnow() - timedelta(days=30):
            cooldown_timestamp = (last_change.timestamp + timedelta(days=30)).strftime('%d.%m.%Y, %H:%M:%S')
            flash(lazy_gettext('You can only change your username once per month. You need to wait until: ') + cooldown_timestamp + ' UTC.', 'danger')
            return render_template('security/change_username.html', change_username_form=form, title=lazy_gettext('Change username'))

        flash(lazy_gettext('Username changed.'))
        username_change = UsernameChange(
            user=current_user.id,
            old_name=user.username,
            new_name=form.username.data,
            timestamp=datetime.utcnow(),
        )
        db.session.add(username_change)
        user.username = form.username.data    
        db.session.commit()

    return render_template('security/change_username.html', change_username_form=form, title=lazy_gettext('Change username'))
