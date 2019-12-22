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

def createStatsObject():
    """
    creates the default stats objects
    """
    return {'darts_thrown': 0, 'double_thrown': 0, 'legs_won': 0, 'total_score': 0, 'average': 0, 'first9_scores': [], 'first9_average': 0, 'doubles': 0, 'number_of_games': 0, 'twenty_and_more': 0, 'forty_and_more': 0}

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

    currentStats['number_of_games'] += 1
    currentStats['darts_thrown'] += len(match_player_legstats_json['scores']) * 3
    for score in match_player_legstats_json['scores']:
        round += 1
        if round <= 3:
            currentStats['first9_scores'].append(score)
        if score > 20:
            currentStats['twenty_and_more'] += 1
        if score > 40:
            currentStats['forty_and_more'] += 1
        currentStats['total_score'] += score
    if 'to_finish' in match_player_legstats_json:
        currentStats['darts_thrown'] -= (3 - match_player_legstats_json['to_finish'])
        currentStats['double_thrown'] += 1
        currentStats['legs_won'] += 1
    if isinstance(match_player_legstats_json['double_missed'], (list,)):
        currentStats['double_thrown'] += sum(match_player_legstats_json['double_missed'])
    else:
        # legacy: double_missed as int
        currentStats['double_thrown'] += match_player_legstats_json['double_missed']
    return currentStats
