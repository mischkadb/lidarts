from flask import render_template
from lidarts.auth import bp


@bp.route('/login')
def login():
    return render_template('auth/login.html')


@bp.route('/register')
def register():
    return render_template('auth/register.html')

