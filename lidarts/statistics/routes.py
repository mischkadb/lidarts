"""
routing functions for statistics
"""

from datetime import timedelta, datetime

import json

from flask_login import current_user, login_required
from flask import render_template
from sqlalchemy import desc
from lidarts.models import User, Game
from lidarts.statistics import bp
from lidarts.statistics.utils import calculate_overall_stats_from_leg, sum_up_stats
from lidarts.statistics.utils import calculate_overall_stats_from_game, create_stats_object
from lidarts.statistics.forms import StatisticsForm


@bp.route('/x01', methods=['GET', 'POST'])
@login_required
def x01():
    form = StatisticsForm()

    stats = {'today': create_stats_object(), 'currentweek': create_stats_object(),
             'currentmonth': create_stats_object(), 'currentyear': create_stats_object(),
             'overall': create_stats_object(), 'custom': create_stats_object(), 'averagepergame': []}

    user = User.query.filter(User.id == current_user.id).first_or_404()

    # if (form.is_submitted):
    custom_filter_number_of_games = form.number_of_games.default
    custom_filter_date_from = form.date_from.default
    custom_filter_date_to = form.date_to.default

    # if no value is in the form data, we can insert the default values
    if form.game_types.data is None:
        form.game_types.data = form.game_types.default
    if form.in_mode.data is None:
        form.in_mode.data = form.in_mode.default
    if form.out_mode.data is None:
        form.out_mode.data = form.out_mode.default
    if form.opponents.data is None:
        form.opponents.data = form.opponents.default
    if form.computer_level.data is None:
        form.computer_level.data = form.computer_level.default
    if form.number_of_games.data is None:
        form.number_of_games.data = custom_filter_number_of_games
    if form.date_from.data is None:
        form.date_from.data = custom_filter_date_from
    if form.date_to.data is None:
        form.date_to.data = custom_filter_date_to

    # check which custom filter is active
    use_custom_filter_last_games = False
    use_custom_filter_date_range = False
    if form.select_game_range_filter.data == 'lastgames':
        use_custom_filter_last_games = True
        custom_filter_number_of_games = form.number_of_games.data
    elif form.select_game_range_filter.data == 'daterange':
        use_custom_filter_date_range = True
        custom_filter_date_from = form.date_from.data
        custom_filter_date_to = form.date_to.data
    else:
        use_custom_filter_last_games = True

    # select the the games (descending order - to be able to filter for last ... games)
    query = Game.query.filter(((Game.player1 == user.id) | (Game.player2 == user.id))
                              & (Game.status == 'completed')
                              & (Game.type == form.game_types.data)
                              & (Game.in_mode == form.in_mode.data)
                              & (Game.out_mode == form.out_mode.data))

    # opponent filter
    if form.opponents.data == 'local':
        query = query.filter(Game.opponent_type == 'local')
    elif form.opponents.data == 'computer':
        if form.computer_level.data == 'all':
            # filter for all computer opponents
            query = query.filter(Game.opponent_type.startswith('computer'))
        else:
            # filter for specific computer level
            query = query.filter(Game.opponent_type == ('computer' + str(form.computer_level.data)))
    elif form.opponents.data == 'online':
        query = query.filter(Game.opponent_type == 'online')

        # check if we must filter to games for one specific user
        if not form.opponent_name.data is None:
            opponent_user_name = str(form.opponent_name.data)
            if opponent_user_name:
                opponent_id = -1
                # check if username is valid and if the user id is not our own user id
                opponent_user = User.query.filter(User.username == opponent_user_name).first()
                if (opponent_user is not None and opponent_user.id is not current_user.id):
                    opponent_id = opponent_user.id

                query = query.filter((Game.player1 == opponent_id) | (Game.player2 == opponent_id))

    # execute the query
    games = query.order_by(desc(Game.begin)).all()

    # get the dates for date related statistics
    today_date = datetime.today().date()
    start_current_week = today_date - timedelta(days=today_date.weekday())
    start_current_month = today_date.replace(day=1)

    number_of_games = 0
    # iterate through each game
    for game in games:
        # hack for legacy games on lidarts.org which do not have double-missed and finish darts
        if game.id < 18:
            continue

        game_begin_date = game.begin.date()

        player = '1'
        if not user.id == game.player1:
            player = '2'

        number_of_games += 1

        # check if game is valid for the current custom filter settings
        valid_game_for_custom_filter = False
        if use_custom_filter_last_games and number_of_games <= custom_filter_number_of_games:
            valid_game_for_custom_filter = True
        elif use_custom_filter_date_range and custom_filter_date_from <= game_begin_date <= custom_filter_date_to:
            valid_game_for_custom_filter = True

        # custom filter
        if valid_game_for_custom_filter:
            calculate_overall_stats_from_game(stats['custom'], game, player)

        # use for today statistics?
        if game_begin_date == today_date:
            calculate_overall_stats_from_game(stats['today'], game, player)

        # use current week statistics?
        if game_begin_date >= start_current_week:
            calculate_overall_stats_from_game(stats['currentweek'], game, player)

        # use current month statistics?
        if game_begin_date >= start_current_month:
            calculate_overall_stats_from_game(stats['currentmonth'], game, player)

        # use current year statistics?
        if game_begin_date.year >= today_date.year:
            calculate_overall_stats_from_game(stats['currentyear'], game, player)

        # overall stats
        calculate_overall_stats_from_game(stats['overall'], game, player)

        match_json = json.loads(game.match_json)

        # calculate current game stats
        current_game_stats = {'darts_thrown': 0, 'total_score': 0}

        # iterate through each set/leg
        for current_set in match_json:
            for current_leg in match_json[current_set]:
                current_player_leg_stats = match_json[current_set][current_leg][player]

                # add stats for current game
                current_game_stats['darts_thrown'] += len(
                    current_player_leg_stats['scores']) * 3
                current_game_stats['total_score'] += sum(
                    current_player_leg_stats['scores'])
                if 'to_finish' in current_player_leg_stats:
                    current_game_stats['darts_thrown'] -= (
                        3 - current_player_leg_stats['to_finish'])

                # custom filter
                if valid_game_for_custom_filter:
                    calculate_overall_stats_from_leg(
                        stats['custom'], current_player_leg_stats)

                # use for today statistics?
                if game_begin_date == today_date:
                    calculate_overall_stats_from_leg(
                        stats['today'], current_player_leg_stats)

                # use current week statistics?
                if game_begin_date >= start_current_week:
                    calculate_overall_stats_from_leg(
                        stats['currentweek'], current_player_leg_stats)

                # use current month statistics?
                if game_begin_date >= start_current_month:
                    calculate_overall_stats_from_leg(
                        stats['currentmonth'], current_player_leg_stats)

                # use current year statistics?
                if game_begin_date.year >= today_date.year:
                    calculate_overall_stats_from_leg(
                        stats['currentyear'], current_player_leg_stats)

                # overall stats
                calculate_overall_stats_from_leg(
                    stats['overall'], current_player_leg_stats)

        # sum up average per game stats
        game_average = round((current_game_stats['total_score'] / (current_game_stats['darts_thrown'])) * 3, 2) \
            if current_game_stats['darts_thrown'] else 0
        stats['averagepergame'].append(game_average)

    # sum up all the stats
    sum_up_stats(stats['custom'])
    sum_up_stats(stats['today'])
    sum_up_stats(stats['currentweek'])
    sum_up_stats(stats['currentmonth'])
    sum_up_stats(stats['currentyear'])
    sum_up_stats(stats['overall'])

    # invert the list for averagepergame (we need the date from the oldest game to newest game)
    stats['averagepergame'].reverse()

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
