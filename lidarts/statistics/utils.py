"""
utility functions for statistics
"""

import json

from datetime import timedelta, datetime
from sqlalchemy import desc
from flask_login import current_user
from lidarts.models import User, Game


def sum_up_stats(stats):
    """
    produces aggregated statistics

    Parameters
    ----------
    stats : []
        dictionary with stats, created by calculateOverallStatsFromLeg
    """

    # print("LEN STATS: " + str(len(stats['first9_scores'])))

    stats['doubles'] = round((stats['legs_won'] / stats['double_thrown']), 4) * 100 \
        if stats['double_thrown'] else 0
    stats['average'] = round((stats['total_score'] / (stats['darts_thrown'])) * 3, 2) \
        if stats['darts_thrown'] else 0
    stats['first9_average'] = round((sum(stats['first9_scores']) / len(stats['first9_scores'])), 2) \
        if stats['first9_scores'] else 0
    stats['first6_average'] = round((sum(stats['first6_scores']) / len(stats['first6_scores'])), 2) \
        if stats['first6_scores'] else 0
    stats['first3_average'] = round((sum(stats['first3_scores']) / len(stats['first3_scores'])), 2) \
        if stats['first3_scores'] else 0

    stats['legs_lost'] = stats['number_of_legs'] - stats['legs_won']

    # calculate games percent
    if stats['number_of_games'] > 0:
        stats['games_won_percent'] = round(
            (stats['games_won'] / stats['number_of_games']) * 100, 2)
        stats['games_lost_percent'] = round(
            (stats['games_lost'] / stats['number_of_games']) * 100, 2)
        stats['games_draw_percent'] = round(
            (stats['games_draw'] / stats['number_of_games']) * 100, 2)

    # calculate legs percent
    if stats['number_of_legs'] > 0:
        stats['legs_won_percent'] = round(
            (stats['legs_won'] / stats['number_of_legs']) * 100, 2)
        stats['legs_lost_percent'] = round(
            (stats['legs_lost'] / stats['number_of_legs']) * 100, 2)

    # calculate scorring percent
    if stats['number_of_rounds'] > 0:
        stats['less_than_twenty_percent'] = round(
            (stats['less_than_twenty'] / stats['number_of_rounds']) * 100, 2)
        stats['twenty_and_more_percent'] = round(
            (stats['twenty_and_more'] / stats['number_of_rounds']) * 100, 2)
        stats['forty_and_more_percent'] = round(
            (stats['forty_and_more'] / stats['number_of_rounds']) * 100, 2)
        stats['sixty_and_more_percent'] = round(
            (stats['sixty_and_more'] / stats['number_of_rounds']) * 100, 2)
        stats['eigthy_and_more_percent'] = round(
            (stats['eigthy_and_more'] / stats['number_of_rounds']) * 100, 2)
        stats['hundred_and_more_percent'] = round(
            (stats['hundred_and_more'] / stats['number_of_rounds']) * 100, 2)
        stats['hundredforty_and_more_percent'] = round(
            (stats['hundredforty_and_more'] / stats['number_of_rounds']) * 100, 2)
        stats['hundredeighty_percent'] = round(
            (stats['hundredeighty'] / stats['number_of_rounds']) * 100, 2)

    # calculate finish percent
    if stats['legs_won'] > 0:
        stats['finish_two_to_forty_percent'] = round(
            (stats['finish_two_to_forty'] / stats['legs_won']) * 100, 2)
        stats['finish_fortyone_to_eigthy_percent'] = round(
            (stats['finish_fortyone_to_eigthy'] / stats['legs_won']) * 100, 2)
        stats['finish_eightyone_to_hundred_percent'] = round(
            (stats['finish_eightyone_to_hundred'] / stats['legs_won']) * 100, 2)
        stats['finish_hundredone_to_hundredtwenty_percent'] = round(
            (stats['finish_hundredone_to_hundredtwenty'] / stats['legs_won']) * 100, 2)
        stats['finish_hundredtwentyone_to_hundredforty_percent'] = round(
            (stats['finish_hundredtwentyone_to_hundredforty'] / stats['legs_won']) * 100, 2)
        stats['finish_hundredfortyone_to_hundredseventy_percent'] = round(
            (stats['finish_hundredfortyone_to_hundredseventy'] / stats['legs_won']) * 100, 2)


def create_stats_object():
    """
    creates the default stats objects
    """
    return {'darts_thrown': 0, 'double_thrown': 0, 'legs_won': 0, 'total_score': 0, 'average': 0,
            'first9_scores': [], 'first9_average': 0, 'doubles': 0, 'number_of_games': 0,
            'shortest_leg': 0, 'number_of_legs': 0, 'legs_lost': 0, 'first6_scores': [], 'first6_average': 0,
            'first3_scores': [], 'first3_average': 0, 'twenty_and_more': 0, 'forty_and_more': 0,
            'sixty_and_more': 0, 'games_won': 0, 'games_lost': 0, 'games_draw': 0,
            'games_won_percent': 0, 'games_lost_percent': 0, 'games_draw_percent': 0,
            'legs_won_percent': 0, 'legs_lost_percent': 0, 'less_than_twenty': 0,
            'eigthy_and_more': 0, 'hundred_and_more': 0, 'less_than_twenty_percent': 0,
            'hundredforty_and_more': 0, 'hundredeighty': 0, 'number_of_rounds': 0,
            'twenty_and_more_percent': 0, 'forty_and_more_percent': 0, 'sixty_and_more_percent': 0,
            'eigthy_and_more_percent': 0, 'hundred_and_more_percent': 0,
            'hundredforty_and_more_percent': 0, 'hundredeighty_percent': 0,
            'highest_finish': 0, 'finish_two_to_forty': 0, 'finish_fortyone_to_eigthy': 0,
            'finish_eightyone_to_hundred': 0, 'finish_hundredone_to_hundredtwenty': 0,
            'finish_hundredtwentyone_to_hundredforty': 0,
            'finish_hundredfortyone_to_hundredseventy': 0,
            'finish_two_to_forty_percent': 0, 'finish_fortyone_to_eigthy_percent': 0,
            'finish_eightyone_to_hundred_percent': 0,
            'finish_hundredone_to_hundredtwenty_percent': 0,
            'finish_hundredtwentyone_to_hundredforty_percent': 0,
            'finish_hundredfortyone_to_hundredseventy_percent': 0}


def calculate_overall_stats_from_game(current_stats, game, player):
    """
    this function calculates the overall stats from for the current game
    """
    current_stats['number_of_games'] += 1

    # draw?
    if game.p1_legs == game.p2_legs:
        current_stats['games_draw'] += 1
    # is player1 the current player?
    elif player == '1':
        if game.p1_legs > game.p2_legs:
            current_stats['games_won'] += 1
        elif game.p1_legs < game.p2_legs:
            current_stats['games_lost'] += 1
    # is player2 the current player?
    elif player == '2':
        if game.p2_legs > game.p1_legs:
            current_stats['games_won'] += 1
        elif game.p2_legs < game.p1_legs:
            current_stats['games_lost'] += 1

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
    current_stats['number_of_legs'] += 1
    darts_thrown_this_leg = len(match_player_legstats_json['scores']) * 3

    score = 0
    for score in match_player_legstats_json['scores']:
        current_round += 1
        if current_round <= 1:
            current_stats['first3_scores'].append(score)
        if current_round <= 2:
            current_stats['first6_scores'].append(score)
        if current_round <= 3:
            current_stats['first9_scores'].append(score)

        current_stats['number_of_rounds'] += 1

        if score == 180:
            current_stats['hundredeighty'] += 1
        elif score >= 140:
            current_stats['hundredforty_and_more'] += 1
        elif score >= 100:
            current_stats['hundred_and_more'] += 1
        elif score >= 80:
            current_stats['eigthy_and_more'] += 1
        elif score >= 60:
            current_stats['sixty_and_more'] += 1
        elif score >= 40:
            current_stats['forty_and_more'] += 1
        elif score >= 20:
            current_stats['twenty_and_more'] += 1
        else:
            current_stats['less_than_twenty'] += 1
        current_stats['total_score'] += score

    # check if player has finished the game
    if 'to_finish' in match_player_legstats_json:
        darts_thrown_this_leg -= (3 -
                                  match_player_legstats_json['to_finish'])
        current_stats['double_thrown'] += 1
        current_stats['legs_won'] += 1

        # check if we can update the shortest leg
        if current_stats['shortest_leg'] == 0 or current_stats['shortest_leg'] > darts_thrown_this_leg:
            current_stats['shortest_leg'] = darts_thrown_this_leg

        if score > current_stats['highest_finish']:
            current_stats['highest_finish'] = score
        if 2 <= score <= 40:
            current_stats['finish_two_to_forty'] += 1
        elif 41 <= score <= 80:
            current_stats['finish_fortyone_to_eigthy'] += 1
        elif 81 <= score <= 100:
            current_stats['finish_eightyone_to_hundred'] += 1
        elif 101 <= score <= 120:
            current_stats['finish_hundredone_to_hundredtwenty'] += 1
        elif 121 <= score <= 140:
            current_stats['finish_hundredtwentyone_to_hundredforty'] += 1
        elif score > 141:
            current_stats['finish_hundredfortyone_to_hundredseventy'] += 1

    if isinstance(match_player_legstats_json['double_missed'], (list,)):
        current_stats['double_thrown'] += sum(
            match_player_legstats_json['double_missed'])
    else:
        # legacy: double_missed as int
        current_stats['double_thrown'] += match_player_legstats_json['double_missed']

    current_stats['darts_thrown'] += darts_thrown_this_leg

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
    stats = {'today': create_stats_object(), 'currentweek': create_stats_object(),
             'currentmonth': create_stats_object(), 'currentyear': create_stats_object(),
             'overall': create_stats_object(), 'custom': create_stats_object(), 'averagepergame': []}

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
