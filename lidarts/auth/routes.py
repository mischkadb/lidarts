from flask import render_template, flash, url_for, redirect
from lidarts.auth import bp
from lidarts.auth.forms import LoginForm, RegistrationForm
from lidarts import db
from lidarts.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}.'.format(form.username.data))
        return redirect(url_for('generic.index'))
    return render_template('auth/login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome to lidarts {}. Thank you for registering.'.format(form.username.data))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

