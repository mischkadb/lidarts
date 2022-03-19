"""
utility functions for statistics
"""

import json

from datetime import timedelta, datetime
from sqlalchemy import desc
from flask_login import current_user
from lidarts import socketio
from lidarts.models import User, Game
from lidarts.statistics.model import Statistics


def calc_percentage(numerator, divisor, precision=2):
    return round((numerator / divisor) * 100, precision)


def sum_up_stats(stats):
    """
    produces aggregated statistics

    Parameters
    ----------
    stats : []
        dictionary with stats, created by calculateOverallStatsFromLeg
    """

    # print("LEN STATS: " + str(len(stats.first9_scores)))

    if stats.double_thrown:
        stats.doubles = calc_percentage(stats.legs_won, stats.double_thrown, 4)
    if stats.darts_thrown:
        stats.average = round((stats.total_score / (stats.darts_thrown)) * 3, 2)
    for first_x, scores in stats.first['scores'].items():
        if not scores:
            continue
        stats.first['averages'][first_x] = round((sum(scores) / len(scores)), 2)

    stats.legs_lost = stats.number_of_legs - stats.legs_won

    # calculate games percent
    if stats.number_of_games > 0:
        for result_type, amount in stats.games['record'].items():
            stats.games['percentages'][result_type] = calc_percentage(amount, stats.number_of_games)

    # calculate legs percent
    if stats.number_of_legs > 0:
        stats.legs_won_percent = calc_percentage(stats.legs_won, stats.number_of_legs)
        stats.legs_lost_percent = calc_percentage(stats.legs_lost, stats.number_of_legs)

    # calculate scorring percent
    number_of_rounds = stats.number_of_rounds
    if number_of_rounds:
        for score_range, score_amount in stats.scoring['ranges'].items():
            stats.scoring['percentages'][score_range] = calc_percentage(score_amount, number_of_rounds)

    # calculate finish percent
    if stats.legs_won > 0:
        for finishing_range, finish_amount in stats.finishing['ranges'].items():
            stats.finishing['percentages'][finishing_range] = calc_percentage(finish_amount, stats.legs_won)


def calculate_overall_stats_from_game(current_stats, game, player):
    """
    this function calculates the overall stats from for the current game
    """
    current_stats.number_of_games += 1
    record = current_stats.games['record']

    # draw?
    if game.p1_sets == game.p2_sets:
        record['draws'] += 1
    # is player1 the current player?
    elif player == '1':
        if game.p1_sets > game.p2_sets:
            record['wins'] += 1
        elif game.p1_sets < game.p2_sets:
            record['losses'] += 1
    # is player2 the current player?
    elif player == '2':
        if game.p2_sets > game.p1_sets:
            record['wins'] += 1
        elif game.p2_sets < game.p1_sets:
            record['losses'] += 1

    return current_stats


def calculate_overall_stats_from_leg(current_stats, match_player_legstats_json):
    """
    calculates overall stats from leg data

    Parameters
    ----------
    current_stats : []
        dictionary with the current stats, created by calculateOverallStatsFromLeg

    match_player_legstats_json : []
        json file with the player data from a leg
    """

    current_round = 0
    current_stats.number_of_legs += 1
    darts_thrown_this_leg = len(match_player_legstats_json['scores']) * 3

    score = 0
    for score in match_player_legstats_json['scores']:
        current_round += 1
        if current_round <= 1:
            current_stats.first['scores']['first3'].append(score)
        if current_round <= 2:
            current_stats.first['scores']['first6'].append(score)
        if current_round <= 3:
            current_stats.first['scores']['first9'].append(score)

        current_stats.number_of_rounds += 1
        scoring_ranges = current_stats.scoring['ranges']

        if score == 180:
            scoring_ranges['180'] += 1
        elif score >= 140:
            scoring_ranges['over_140'] += 1
        elif score >= 100:
            scoring_ranges['over_100'] += 1
        elif score >= 80:
            scoring_ranges['over_80'] += 1
        elif score >= 60:
            scoring_ranges['over_60'] += 1
        elif score >= 40:
            scoring_ranges['over_40'] += 1
        elif score >= 20:
            scoring_ranges['over_20'] += 1
        else:
            scoring_ranges['under_20'] += 1

        # for 19s
        if 180 > score >= 171:
            scoring_ranges['over_171'] += 1
        elif score >= 131:
            scoring_ranges['over_131'] += 1
        elif score >= 91:
            scoring_ranges['over_91'] += 1
        elif score >= 57:
            scoring_ranges['over_57'] += 1
        elif score >= 40:
            scoring_ranges['over_40_19s'] += 1
        current_stats.total_score += score

    # check if player has finished the game
    if 'to_finish' in match_player_legstats_json:
        darts_thrown_this_leg -= (3 -
                                  match_player_legstats_json['to_finish'])
        current_stats.double_thrown += 1
        current_stats.legs_won += 1

        # check if we can update the shortest leg
        if current_stats.shortest_leg == 0 or current_stats.shortest_leg > darts_thrown_this_leg:
            current_stats.shortest_leg = darts_thrown_this_leg

        if score > current_stats.highest_finish:
            current_stats.highest_finish = score
        finishing_ranges = current_stats.finishing['ranges']
        if 2 <= score <= 40:
            finishing_ranges['range_2_40'] += 1
        elif 41 <= score <= 80:
            finishing_ranges['range_41_80'] += 1
        elif 81 <= score <= 100:
            finishing_ranges['range_81_100'] += 1
        elif 101 <= score <= 120:
            finishing_ranges['range_101_120'] += 1
        elif 121 <= score <= 140:
            finishing_ranges['range_121_140'] += 1
        elif score > 141:
            finishing_ranges['range_141_170'] += 1

    if isinstance(match_player_legstats_json['double_missed'], (list,)):
        current_stats.double_thrown += sum(
            match_player_legstats_json['double_missed'])
    else:
        # legacy: double_missed as int
        current_stats.double_thrown += match_player_legstats_json['double_missed']

    current_stats.darts_thrown += darts_thrown_this_leg

    return current_stats


def calculate_set_leg_statistics(match_json, player, current_game_stats, valid_game_for_custom_filter, stats,
                                 game_begin_date, today_date, start_current_week, start_current_month):
    """
    this function calculates the set and leg statistics for a match
    """
    for current_set in match_json:
        for current_leg in match_json[current_set]:
            current_player_leg_stats = match_json[current_set][current_leg][player]

            # add stats for current game
            current_game_stats['darts_thrown'] += len(
                current_player_leg_stats['scores']) * 3
            current_game_stats['total_score'] += sum(current_player_leg_stats['scores'])
            if 'to_finish' in current_player_leg_stats:
                current_game_stats['darts_thrown'] -= (3 - current_player_leg_stats['to_finish'])

            # custom filter
            if valid_game_for_custom_filter:
                calculate_overall_stats_from_leg(stats['custom'], current_player_leg_stats)

            # use for today statistics?
            if game_begin_date == today_date:
                calculate_overall_stats_from_leg(stats['today'], current_player_leg_stats)

            # use current week statistics?
            if game_begin_date >= start_current_week:
                calculate_overall_stats_from_leg(stats['currentweek'], current_player_leg_stats)

            # use current month statistics?
            if game_begin_date >= start_current_month:
                calculate_overall_stats_from_leg(stats['currentmonth'], current_player_leg_stats)

            # use current year statistics?
            if game_begin_date.year >= today_date.year:
                calculate_overall_stats_from_leg(stats['currentyear'], current_player_leg_stats)

            # overall stats
            calculate_overall_stats_from_leg(stats['overall'], current_player_leg_stats)


def create_statistics_query(user, form):
    """
    this function builds the database query
    """
    # basic query
    query = Game.query.filter(((Game.player1 == user.id) | (Game.player2 == user.id))
                              & (Game.status == 'completed')
                              & (Game.type == form.game_types.data)
                              & (Game.in_mode == form.in_mode.data)
                              & (Game.out_mode == form.out_mode.data))

    # check if we need the opponent filter
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
        opponent_user_name = str(form.opponent_name.data)
        if opponent_user_name:
            opponent_id = 0
            # try to get user from database
            opponent_user = User.query.filter(User.username == opponent_user_name).first()

            # check if username is valid (found in database) and if the user id is not our own user id
            if opponent_user is not None and opponent_user.id != current_user.id:
                opponent_id = opponent_user.id

            query = query.filter((Game.player1 == opponent_id) | (Game.player2 == opponent_id))

    # execute the query (descending order - to be able to filter for last ... games)
    return query.order_by(desc(Game.begin))


def create_statistics(user, form, use_custom_filter_last_games, use_custom_filter_date_range):
    """
    this function builds the statistics for the given games and filter criterias
    """

    # build the query and select the the games
    games = create_statistics_query(user, form).all()

    # create the stats object
    stats = {'today': Statistics(), 'currentweek': Statistics(),
             'currentmonth': Statistics(), 'currentyear': Statistics(),
             'overall': Statistics(), 'custom': Statistics(), 'averagepergame': []}

    # get the dates for date related statistics
    today_date = datetime.today().date()
    start_current_week = today_date - timedelta(days=today_date.weekday())
    start_current_month = today_date.replace(day=1)

    number_of_games = 0
    # iterate through each game
    for game in games:
        socketio.sleep(0)
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
        if use_custom_filter_last_games and number_of_games <= form.number_of_games.data:
            valid_game_for_custom_filter = True
        elif use_custom_filter_date_range and form.date_from.data <= game_begin_date <= form.date_to.data:
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

        # iterate through each set/leg and calculate the corresponding statistics
        calculate_set_leg_statistics(match_json, player, current_game_stats, valid_game_for_custom_filter, stats,
                                     game_begin_date, today_date, start_current_week, start_current_month)

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

    return stats
