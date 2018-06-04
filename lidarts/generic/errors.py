from flask import render_template
from lidarts import db


def not_found_error(error):
    return render_template('generic/404.html'), 404


def internal_error(error):
    db.session.rollback()
    return render_template('generic/500.html'), 500
