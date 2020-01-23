"""
routing functions for statistics
"""

from flask_login import current_user, login_required
from flask import render_template
from lidarts.models import User
from lidarts.statistics import bp
from lidarts.statistics.utils import create_statistics
from lidarts.statistics.forms import StatisticsForm


@bp.route('/x01', methods=['GET', 'POST'])
@login_required
def x01():
    """ this function get's all required data for the statistics """
    form = StatisticsForm()

    user = User.query.filter(User.id == current_user.id).first_or_404()

    # check which custom filter is active
    use_custom_filter_last_games = False
    use_custom_filter_date_range = False
    if form.select_game_range_filter.data == 'lastgames':
        use_custom_filter_last_games = True
    elif form.select_game_range_filter.data == 'daterange':
        use_custom_filter_date_range = True
    else:
        use_custom_filter_last_games = True

    # get the dates for date related statistics
    stats = create_statistics(user, form, use_custom_filter_last_games, use_custom_filter_date_range)

    # style for some ui elements
    computer_level_displaystyle = 'none'
    opponent_name_displaystyle = 'none'

    # if we are in post (from filter), we must append the prefix for the internal link
    if form.is_submitted():
        if form.opponents.data == 'computer':
            computer_level_displaystyle = 'block'
        elif form.opponents.data == 'online':
            opponent_name_displaystyle = 'block'

    return render_template('statistics/x01.html', stats=stats, form=form,
                           computer_level_displaystyle=computer_level_displaystyle,
                           opponent_name_displaystyle=opponent_name_displaystyle)
