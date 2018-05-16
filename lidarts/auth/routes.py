from flask import render_template, flash, url_for, redirect
from lidarts.auth import bp
from lidarts.auth.forms import LoginForm


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}.'.format(form.username.data))
        return redirect(url_for('generic.index'))
    return render_template('auth/login.html', form=form)


@bp.route('/register')
def register():
    return render_template('auth/register.html')

