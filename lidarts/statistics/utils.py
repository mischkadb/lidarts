"""
utility functions for statistics
"""


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
            'number_of_legs': 0, 'legs_lost': 0, 'first6_scores': [], 'first6_average': 0,
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

        if score < 20:
            current_stats['less_than_twenty'] += 1
        if score >= 20:
            current_stats['twenty_and_more'] += 1
        if score >= 40:
            current_stats['forty_and_more'] += 1
        if score >= 60:
            current_stats['sixty_and_more'] += 1
        if score >= 80:
            current_stats['eigthy_and_more'] += 1
        if score >= 100:
            current_stats['hundred_and_more'] += 1
        if score >= 140:
            current_stats['hundredforty_and_more'] += 1
        if score == 180:
            current_stats['hundredeighty'] += 1
        current_stats['total_score'] += score

    # check if player has finished the game
    if 'to_finish' in match_player_legstats_json:
        darts_thrown_this_leg -= (3 -
                                  match_player_legstats_json['to_finish'])
        current_stats['double_thrown'] += 1
        current_stats['legs_won'] += 1

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
