from flask import render_template
from lidarts.profile import bp
from lidarts.models import User


@bp.route('/@/<username>')
def overview(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile/overview.html', user=user)
