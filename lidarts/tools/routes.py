from flask import render_template, request, redirect, url_for
from lidarts import db
from lidarts.tools import bp
from lidarts.tools.forms import BoardCoordinateForm
from lidarts.models import BoardCoordinates
from flask_login import current_user, login_required


@bp.route('/board', methods=['GET', 'POST'])
@login_required
def board():
    player = current_user.id if current_user.is_authenticated else None
    form = BoardCoordinateForm(request.form)
    if form.validate_on_submit():
        x1 = form.x1.data
        y1 = form.y1.data
        x2 = form.x2.data
        y2 = form.y2.data
        x3 = form.x3.data
        y3 = form.y3.data
        board_coords = BoardCoordinates(user=player, x1=x1, y1=y1, x2=x2, y2=y2, x3=x3, y3=y3)
        db.session.add(board_coords)
        db.session.commit()
        return redirect(url_for('tools.board'))
    if request.method == 'POST' and not form.validate():
        return redirect(url_for('tools.board'))
    return render_template('tools/board.html', form=form)
