from flask import render_template, flash, url_for, redirect
from flask_login import current_user, login_user, logout_user
from lidarts.auth import bp
from lidarts.auth.forms import LoginForm, RegistrationForm
from lidarts import db
from lidarts.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # make sure logged in users cannot access the login page again
    if current_user.is_authenticated:
        return redirect(url_for('generic.lobby'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username.ilike(form.username.data)).first()
        # incorrect username or password handling
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('auth.login'))
        # remember_me is currently not implemented (easy though), see issue #3
        login_user(user, remember=False)
        flash('Hello {}. You successfully logged in.'.format(user.username))
        return redirect(url_for('generic.index'))
    return render_template('auth/login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # logged in users should not come here
    if current_user.is_authenticated:
        return redirect(url_for('generic.lobby'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        # password hashing
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome to lidarts {}. Thank you for registering.'.format(form.username.data))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    flash('Logout successful.')
    return redirect(url_for('generic.index'))

