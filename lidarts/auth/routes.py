from flask import render_template, flash
from flask_login import current_user
from flask_babelex import lazy_gettext
from lidarts import db
from lidarts.auth import bp
from lidarts.auth.forms import ChangeUsernameForm
from lidarts.models import User


@bp.route('/change_username', methods=['GET', 'POST'])
def change_username():
    # logged in users do not need the index page
    form = ChangeUsernameForm()
    user = User.query.filter_by(id=current_user.id).first_or_404()

    if form.validate_on_submit():
        flash(lazy_gettext('Username changed.'))
        user.username = form.username.data
        db.session.commit()

    return render_template('security/change_username.html', change_username_form=form, title=lazy_gettext('Change username'))
