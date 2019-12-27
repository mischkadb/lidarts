def sumUpStats(currentStats):
    """
    produces aggregated statistics

    Parameters
    ----------
    currentStats : []
        dictionary with stats, created by calculateOverallStatsFromLeg
    """
    currentStats['doubles'] = round((currentStats['legs_won'] / currentStats['double_thrown']), 4) * 100 if currentStats['double_thrown'] else 0
    currentStats['average'] = round((currentStats['total_score'] / (currentStats['darts_thrown'])) * 3, 2) if currentStats['darts_thrown'] else 0
    currentStats['first9_average'] = round((sum(currentStats['first9_scores']) / len(currentStats['first9_scores'])), 2) \
        if currentStats['first9_scores'] else 0
    currentStats['first6_average'] = round((sum(currentStats['first6_scores']) / len(currentStats['first6_scores'])), 2) \
        if currentStats['first6_scores'] else 0
    currentStats['first3_average'] = round((sum(currentStats['first3_scores']) / len(currentStats['first3_scores'])), 2) \
        if currentStats['first3_scores'] else 0

    currentStats['legs_lost'] = currentStats['number_of_legs'] - currentStats['legs_won']

    # calculate games percent
    if currentStats['number_of_games'] > 0:
        currentStats['games_won_percent'] = round((currentStats['games_won'] / currentStats['number_of_games']) * 100, 2)
        currentStats['games_lost_percent'] = round((currentStats['games_lost'] / currentStats['number_of_games']) * 100, 2)
        currentStats['games_draw_percent'] = round((currentStats['games_draw'] / currentStats['number_of_games']) * 100, 2)
    
    # calculate legs percent
    if (currentStats['number_of_legs'] > 0):
        currentStats['legs_won_percent'] = round((currentStats['legs_won'] / currentStats['number_of_legs']) * 100, 2)
        currentStats['legs_lost_percent'] = round((currentStats['legs_lost'] / currentStats['number_of_legs']) * 100, 2)

    # calculate scorring percent
    if (currentStats['number_of_rounds'] > 0):
        currentStats['less_than_twenty_percent'] = round((currentStats['less_than_twenty'] / currentStats['number_of_rounds']) * 100, 2)
        currentStats['twenty_and_more_percent'] = round((currentStats['twenty_and_more'] / currentStats['number_of_rounds']) * 100, 2)
        currentStats['forty_and_more_percent'] = round((currentStats['forty_and_more'] / currentStats['number_of_rounds']) * 100, 2)
        currentStats['sixty_and_more_percent'] = round((currentStats['sixty_and_more'] / currentStats['number_of_rounds']) * 100, 2)
        currentStats['eigthy_and_more_percent'] = round((currentStats['eigthy_and_more'] / currentStats['number_of_rounds']) * 100, 2)
        currentStats['hundred_and_more_percent'] = round((currentStats['hundred_and_more'] / currentStats['number_of_rounds']) * 100, 2)
        currentStats['hundredforty_and_more_percent'] = round((currentStats['hundredforty_and_more'] / currentStats['number_of_rounds']) * 100, 2)
        currentStats['hundredeighty_percent'] = round((currentStats['hundredeighty'] / currentStats['number_of_rounds']) * 100, 2)

    # calculate finish percent
    if (currentStats['legs_won'] > 0):
        currentStats['finish_two_to_forty_percent'] = round((currentStats['finish_two_to_forty'] / currentStats['legs_won']) * 100, 2)
        currentStats['finish_fortyone_to_eigthy_percent'] = round((currentStats['finish_fortyone_to_eigthy'] / currentStats['legs_won']) * 100, 2)
        currentStats['finish_eightyone_to_hundred_percent'] = round((currentStats['finish_eightyone_to_hundred'] / currentStats['legs_won']) * 100, 2)
        currentStats['finish_hundredone_to_hundredtwenty_percent'] = round((currentStats['finish_hundredone_to_hundredtwenty'] / currentStats['legs_won']) * 100, 2)
        currentStats['finish_hundredtwentyone_to_hundredforty_percent'] = round((currentStats['finish_hundredtwentyone_to_hundredforty'] / currentStats['legs_won']) * 100, 2)
        currentStats['finish_hundredfortyone_to_hundredseventy_percent'] = round((currentStats['finish_hundredfortyone_to_hundredseventy'] / currentStats['legs_won']) * 100, 2)

def createStatsObject():
    """
    creates the default stats objects
    """
    return {'darts_thrown': 0, 'double_thrown': 0, 'legs_won': 0, 'total_score': 0, 'average': 0, 'first9_scores': [], 
            'first9_average': 0, 'doubles': 0, 'number_of_games': 0, 'number_of_legs': 0, 'legs_lost': 0,
            'first6_scores': [], 'first6_average': 0, 'first3_scores': [], 'first3_average': 0,
            'twenty_and_more': 0, 'forty_and_more': 0, 'sixty_and_more': 0, 
            'games_won': 0, 'games_lost': 0, 'games_draw': 0, 'games_won_percent': 0, 'games_lost_percent': 0, 'games_draw_percent': 0,
            'legs_won_percent': 0, 'legs_lost_percent': 0, 'less_than_twenty': 0, 'eigthy_and_more': 0,  'hundred_and_more': 0, 
            'hundredforty_and_more': 0, 'hundredeighty': 0, 'number_of_rounds': 0, 'less_than_twenty_percent': 0, 
            'twenty_and_more_percent': 0, 'forty_and_more_percent': 0, 'sixty_and_more_percent': 0, 'eigthy_and_more_percent': 0,
            'hundred_and_more_percent': 0, 'hundredforty_and_more_percent': 0, 'hundredeighty_percent': 0,
            'highest_finish': 0, 'finish_two_to_forty': 0, 'finish_fortyone_to_eigthy': 0, 'finish_eightyone_to_hundred': 0,
            'finish_hundredone_to_hundredtwenty': 0, 'finish_hundredtwentyone_to_hundredforty': 0, 'finish_hundredfortyone_to_hundredseventy': 0,
            'finish_two_to_forty_percent': 0, 'finish_fortyone_to_eigthy_percent': 0, 'finish_eightyone_to_hundred_percent': 0,
            'finish_hundredone_to_hundredtwenty_percent': 0, 'finish_hundredtwentyone_to_hundredforty_percent': 0, 
            'finish_hundredfortyone_to_hundredseventy_percent': 0}


def calculateOverallStatsFromGame(currentStats, game):
    currentStats['number_of_games'] += 1
    if (game.p1_legs > game.p2_legs):
        currentStats['games_won'] += 1
    elif (game.p1_legs < game.p2_legs):
        currentStats['games_lost'] += 1
    else:
        currentStats['games_draw'] += 1

    return currentStats

def calculateOverallStatsFromLeg(currentStats, match_player_legstats_json):
    """
    calculates overall stats from leg data

    Parameters
    ----------
    currentStats : []
        dictionary with the current stats, created by calculateOverallStatsFromLeg
    
    match_player_legstats_json : []
        json file with the player data from a leg
    """
    
    round = 0
    dartsThrownThisLeg = 0
    currentStats['number_of_legs'] += 1
    dartsThrownThisLeg = len(match_player_legstats_json['scores']) * 3

    for score in match_player_legstats_json['scores']:
        round += 1
        if round <= 1:
            currentStats['first3_scores'].append(score)
        if round <= 2:
            currentStats['first6_scores'].append(score)
        if round <= 3:
            currentStats['first9_scores'].append(score)

        currentStats['number_of_rounds'] += 1

        if score < 20:
            currentStats['less_than_twenty'] += 1
        if score >= 20:
            currentStats['twenty_and_more'] += 1
        if score >= 40:
            currentStats['forty_and_more'] += 1
        if score >= 60:
            currentStats['sixty_and_more'] += 1
        if score >= 80:
            currentStats['eigthy_and_more'] += 1
        if score >= 100:
            currentStats['hundred_and_more'] += 1
        if score >= 140:
            currentStats['hundredforty_and_more'] += 1
        if score == 180:
            currentStats['hundredeighty'] += 1
        currentStats['total_score'] += score
    
    if 'to_finish' in match_player_legstats_json:
        dartsThrownThisLeg -= (3 - match_player_legstats_json['to_finish'])
        currentStats['double_thrown'] += 1
        currentStats['legs_won'] += 1

        if score > currentStats['highest_finish']:
            currentStats['highest_finish'] = score
        if (score > 2 and score <= 40):
            currentStats['finish_two_to_forty'] += 1
        elif (score > 41 and score <= 80):
            currentStats['finish_fortyone_to_eigthy'] += 1
        elif (score > 81 and score <= 100):
            currentStats['finish_eightyone_to_hundred'] += 1
        elif (score > 101 and score <= 120):
            currentStats['finish_hundredone_to_hundredtwenty'] += 1
        elif (score > 121 and score <= 140):
            currentStats['finish_hundredtwentyone_to_hundredforty'] += 1
        elif (score > 141):
            currentStats['finish_hundredfortyone_to_hundredseventy'] += 1


    if isinstance(match_player_legstats_json['double_missed'], (list,)):
        currentStats['double_thrown'] += sum(match_player_legstats_json['double_missed'])
    else:
        # legacy: double_missed as int
        currentStats['double_thrown'] += match_player_legstats_json['double_missed']

    currentStats['darts_thrown'] += dartsThrownThisLeg

    return currentStats
