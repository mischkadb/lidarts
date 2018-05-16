from flask import render_template, flash, url_for, redirect
from flask_login import current_user, login_user, logout_user
from lidarts.auth import bp
from lidarts.auth.forms import LoginForm, RegistrationForm
from lidarts import db
from lidarts.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('generic.lobby'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('auth.login'))
        # remember_me is currently not implemented (easy though), see issue #3
        login_user(user, remember=False)
        flash('Hello {}. You successfully logged in.'.format(form.username.data))
        return redirect(url_for('generic.index'))
    return render_template('auth/login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('generic.lobby'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
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

