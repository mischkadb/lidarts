from lidarts import socketio
from lidarts.models import CricketGame
from collections import deque
import json
import numpy as np

# Level 1: Darts/Leg Avg. 67.353 | Score Avg. 22.315264353480913 | Double% 0.08976660682226212
level1 = {
    'hit_chance_single': [0.1, 0.7, 0.1, 0.1],
    'hit_chance_double': [0.5, 0.4, 0.1, 0],
    'hit_chance_triple': [0.1, 0.7, 0.1, 0.1],
    'hit_chance_D25': [0.05, 0.05, 0.045],
    'hit_chance_S25': [0.05, 0.05, 0.045],
    'hit_chance_field': [0.34, 0.33, 0.33],
    'hit_chance_field_at_double': [0.6, 0.2, 0.2]
}

# Level 2: Darts/Leg Avg. 50.566 | Score Avg. 29.72352964442511 | Double% 0.12471938139186829
level2 = {
    'hit_chance_single': [0.05, 0.75, 0.1, 0.1],
    'hit_chance_double': [0.5, 0.35, 0.15, 0],
    'hit_chance_triple': [0.05, 0.75, 0.05, 0.15],
    'hit_chance_D25': [0.1, 0.1, 0.04],
    'hit_chance_S25': [0.1, 0.1, 0.04],
    'hit_chance_field': [0.4, 0.3, 0.3],
    'hit_chance_field_at_double': [0.7, 0.15, 0.15]
}

# Level 3: Darts/Leg Avg. 38.766 | Score Avg. 38.77108806686272 | Double% 0.17140898183064793
level3 = {
    'hit_chance_single': [0.05, 0.75, 0.1, 0.1],
    'hit_chance_double': [0.5, 0.3, 0.2, 0],
    'hit_chance_triple': [0.05, 0.72, 0.05, 0.18],
    'hit_chance_D25': [0.1, 0.1, 0.04],
    'hit_chance_S25': [0.1, 0.1, 0.04],
    'hit_chance_field': [0.5, 0.25, 0.25],
    'hit_chance_field_at_double': [0.75, 0.125, 0.125]
}

# Level 4: Darts/Leg Avg. 31.775 | Score Avg. 47.30133752950433 | Double% 0.21673168617251842
level4 = {
    'hit_chance_single': [0.02, 0.78, 0.1, 0.1],
    'hit_chance_double': [0.45, 0.3, 0.25, 0],
    'hit_chance_triple': [0, 0.8, 0, 0.2],
    'hit_chance_D25': [0.15, 0.15, 0.035],
    'hit_chance_S25': [0.1, 0.2, 0.035],
    'hit_chance_field': [0.6, 0.2, 0.2],
    'hit_chance_field_at_double': [0.8, 0.1, 0.1]
}

# Level 5: Darts/Leg Avg. 28.282 | Score Avg. 53.14334205501732 | Double% 0.23413720440177943
level5 = {
    'hit_chance_single': [0, 0.8, 0.1, 0.1],
    'hit_chance_double': [0.45, 0.3, 0.25, 0],
    'hit_chance_triple': [0, 0.8, 0, 0.2],
    'hit_chance_D25': [0.15, 0.25, 0.03],
    'hit_chance_S25': [0.1, 0.3, 0.03],
    'hit_chance_field': [0.7, 0.15, 0.15],
    'hit_chance_field_at_double': [0.85, 0.075, 0.075]
}

# Level 6: Darts/Leg Avg. 24.26 | Score Avg. 61.95383347073372 | Double% 0.2788622420524261
level6 = {
    'hit_chance_single': [0, 0.8, 0.1, 0.1],
    'hit_chance_double': [0.5, 0.2, 0.3, 0],
    'hit_chance_triple': [0, 0.75, 0, 0.25],
    'hit_chance_D25': [0.2, 0.3, 0.025],
    'hit_chance_S25': [0.15, 0.35, 0.025],
    'hit_chance_field': [0.75, 0.125, 0.125],
    'hit_chance_field_at_double': [0.9, 0.05, 0.05]
}

# Level 7: Darts/Leg Avg. 22.101 | Score Avg. 68.00597258042622 | Double% 0.2824060999717594
level7 = {
    'hit_chance_single': [0, 0.84, 0.08, 0.08],
    'hit_chance_double': [0.5, 0.15, 0.35, 0],
    'hit_chance_triple': [0, 0.7, 0, 0.3],
    'hit_chance_D25': [0.25, 0.35, 0.02],
    'hit_chance_S25': [0.2, 0.4, 0.02],
    'hit_chance_field': [0.8, 0.1, 0.1],
    'hit_chance_field_at_double': [0.95, 0.025, 0.025]
}

# Level 8: Darts/Leg Avg. 19.29 | Score Avg. 77.91601866251943 | Double% 0.34518467380048323
level8 = {
    'hit_chance_single': [0, 0.86, 0.07, 0.07],
    'hit_chance_double': [0.5, 0.1, 0.4, 0],
    'hit_chance_triple': [0, 0.65, 0, 0.35],
    'hit_chance_D25': [0.3, 0.4, 0.015],
    'hit_chance_S25': [0.25, 0.45, 0.015],
    'hit_chance_field': [0.85, 0.075, 0.075],
    'hit_chance_field_at_double': [0.96, 0.02, 0.02]
}

# Level 9: Darts/Leg Avg. 16.97 | Score Avg. 88.56806128461992 | Double% 0.44603033006244425
level9 = {
    'hit_chance_single': [0, 0.9, 0.05, 0.05],
    'hit_chance_double': [0.4, 0.1, 0.5, 0],
    'hit_chance_triple': [0, 0.6, 0, 0.4],
    'hit_chance_D25': [0.4, 0.4, 0.01],
    'hit_chance_S25': [0.3, 0.5, 0.01],
    'hit_chance_field': [0.9, 0.05, 0.05],
    'hit_chance_field_at_double': [0.97, 0.015, 0.015]
}

levels = [level1, level2, level3, level4, level5, level6, level7, level8, level9]


def get_target(game):
    match_json = json.loads(game.match_json)
    current_set = str(len(match_json))
    current_leg = str(len(match_json[current_set]))
    p1_current_leg_fields = match_json[current_set][current_leg]['1']['fields']
    p2_current_leg_fields = match_json[current_set][current_leg]['2']['fields']
    # naive target selection: close out all fields first, then try to score
    if p2_current_leg_fields['20']['marks'] < 3:
        return 'T20'
    elif p2_current_leg_fields['19']['marks'] < 3:
        return 'T19'
    elif p2_current_leg_fields['18']['marks'] < 3:
        return 'T18'
    elif p2_current_leg_fields['17']['marks'] < 3:
        return 'T17'
    elif p2_current_leg_fields['16']['marks'] < 3:
        return 'T16'
    elif p2_current_leg_fields['15']['marks'] < 3:
        return 'T15'
    elif p2_current_leg_fields['25']['marks'] < 3:
        return 'D25'

    if p1_current_leg_fields['20']['marks'] < 3:
        return 'T20'
    elif p1_current_leg_fields['19']['marks'] < 3:
        return 'T19'
    elif p1_current_leg_fields['18']['marks'] < 3:
        return 'T18'
    elif p1_current_leg_fields['17']['marks'] < 3:
        return 'T17'
    elif p1_current_leg_fields['16']['marks'] < 3:
        return 'T16'
    elif p1_current_leg_fields['15']['marks'] < 3:
        return 'T15'
    elif p1_current_leg_fields['25']['marks'] < 3:
        return 'D25'


def throw_dart(target, computer):
    possible_hits = {}

    # cyclic data structure to simulate the dartboard
    dartboard = deque([20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5])

    field_type = target[0]  # 'S', 'D' or 'T'

    # probabilities to hit: 0 / single / double / triple
    if field_type == 'S':
        hit_chance = computer['hit_chance_single']
    elif field_type == 'D':
        hit_chance = computer['hit_chance_double']
    else:
        hit_chance = computer['hit_chance_triple']

    if target == 'D25':
        # probabilities for double bull
        possible_hits['D25'] = computer['hit_chance_D25'][0]
        possible_hits['S25'] = computer['hit_chance_D25'][1]
        # all numbers have a basic chance to be hit
        for number in range(1, 21):
            field = 'S' + str(number)
            possible_hits[field] = computer['hit_chance_D25'][2]
    elif target == 'S25':
        # probabilities for single bull
        possible_hits['D25'] = computer['hit_chance_S25'][0]
        possible_hits['S25'] = computer['hit_chance_S25'][1]
        # all numbers have a basic chance to be hit
        for number in range(1, 21):
            field = 'S' + str(number)
            possible_hits[field] = computer['hit_chance_S25'][2]
    else:
        # target number
        target_numbers = [int(target[1:])]
        index = dartboard.index(int(target[1:]))

        # get numbers next to target
        dartboard.rotate(-index)
        target_numbers.append(dartboard[-1])
        target_numbers.append(dartboard[1])

        # probability to hit: target / number left / number right
        if field_type == 'D':
            number_hit = str(np.random.choice(target_numbers, p=computer['hit_chance_field_at_double']))
        else:
            number_hit = str(np.random.choice(target_numbers, p=computer['hit_chance_field']))

        possible_hits['0'] = hit_chance[0]
        possible_hits['S' + number_hit] = hit_chance[1]
        possible_hits['D' + number_hit] = hit_chance[2]
        possible_hits['T' + number_hit] = hit_chance[3]

    hit = np.random.choice(list(possible_hits), p=list(possible_hits.values()))

    if hit == '0':
        return 0, '0'
    elif hit[0] == 'S':
        factor = 1
    elif hit[0] == 'D':
        factor = 2
    else:
        factor = 3

    number = int(hit[1:])
    # make sure no collision happens (e.g. D10, T10)
    number = 0 if number < 15 else number

    return number*factor, hit


def get_computer_score(hashid):
    game = CricketGame.query.filter_by(hashid=hashid).first_or_404()

    computer_level = int(game.opponent_type[-1])
    computer = levels[computer_level-1]

    # acquire target depending on game situation
    if game.closest_to_bull:
        thrown_score, field_hit = throw_dart('D25', computer)
        return thrown_score
    else:
        target = get_target(game)

    # simulate dart throw
    thrown_score, field_hit = throw_dart(target, computer)

    return thrown_score
