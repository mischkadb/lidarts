from math import sqrt, atan, degrees, cos, radians
import numpy as np
import time


double_attempts = [0, 0]

# checkout table contains the next field to aim at
checkout_table = {1: {'170': 'T20', '167': 'T20', '164': 'T20', '161': 'T20', '160': 'T20', '158': 'T20',
                      '157': 'T20', '156': 'T20', '155': 'T20', '154': 'T20', '153': 'T20', '152': 'T20',
                      '151': 'T20', '150': 'T20', '149': 'T20', '148': 'T20', '147': 'T20', '146': 'T20',
                      '145': 'T20', '144': 'T20', '143': 'T20', '142': 'T20', '141': 'T20', '140': 'T20',
                      '139': 'T20', '138': 'T20', '137': 'T20', '136': 'T20', '135': 'T20', '134': 'T20',
                      '133': 'T20', '132': 'T20', '131': 'T19', '130': 'T20', '129': 'T19', '128': 'T18',
                      '127': 'T20', '126': 'T19', '125': 'T18', '124': 'T20', '123': 'T19', '122': 'T18',
                      '121': 'T20', '120': 'T20', '119': 'T19', '118': 'T20', '117': 'T19', '116': 'T19',
                      '115': 'T20', '114': 'T19', '113': 'T19', '112': 'T20', '111': 'T19', '110': 'T20',
                      '109': 'T20', '108': 'T20',
                      '107': 'T19', '106': 'T20', '105': 'T20', '104': 'T19', '103': 'T19', '102': 'T20',
                      '101': 'T20', '100': 'T20', '99': 'T19', '98': 'T20', '97': 'T19', '96': 'T20', '95':
                          'T19', '94': 'T18', '93': 'T19', '92': 'T20', '91': 'T17', '90': 'T20', '89': 'T19',
                      '88': 'T20', '87': 'T17', '86': 'T18', '85': 'T15', '84': 'T20', '83': 'T17', '82': 'T14',
                      '81': 'T15', '80': 'T20', '79': 'T19', '78': 'T18', '77': 'T19', '76': 'T20', '75': 'T17',
                      '74': 'T14', '73': 'T19', '72': 'T16', '71': 'T13', '70': 'T18', '69': 'T19', '68': 'T16',
                      '67': 'T9', '66': 'T10', '65': 'T11', '64': 'T16', '63': 'T13', '62': 'T10', '61': 'T15',
                      '60': 'S20', '59': 'S19', '58': 'S18', '57': 'S17', '56': 'T16', '55': 'S15', '54': 'S14',
                      '53': 'S13', '52': 'S12', '51': 'S11', '50': 'S10', '49': 'S9', '48': 'S16', '47': 'S7',
                      '46': 'S6', '45': 'S13', '44': 'S12', '43': 'S3', '42': 'S10', '41': 'S9'},

                  2: {'170': 'T20', '167': 'T20', '164': 'T20', '161': 'T20', '160': 'T20', '158': 'T20',
                      '157': 'T20', '156': 'T20', '155': 'T20', '154': 'T20', '153': 'T20', '152': 'T20',
                      '151': 'T20', '150': 'T20', '149': 'T20', '148': 'T20', '147': 'T20', '146': 'T20',
                      '145': 'T20', '144': 'T20', '143': 'T20', '142': 'T20', '141': 'T20', '140': 'T20',
                      '139': 'T20', '138': 'T20', '137': 'T20', '136': 'T20', '135': 'T20', '134': 'T20',
                      '133': 'T20', '132': 'T20', '131': 'T19', '130': 'T20', '129': 'T19', '128': 'T18',
                      '127': 'T20', '126': 'T19', '125': 'T18', '124': 'T20', '123': 'T19', '122': 'T18',
                      '121': 'T20', '120': 'T20', '119': 'T19', '118': 'T20', '117': 'T19', '116': 'T19',
                      '115': 'T20', '114': 'T19', '113': 'T19', '112': 'T20', '111': 'T19', '110': 'T20',
                      '109': 'T20', '108': 'T20',
                      '107': 'T19', '106': 'T20', '105': 'T20', '104': 'T18', '103': 'T19', '102': 'T20',
                      '101': 'T17', '100': 'T20', '99': 'T19', '98': 'T20', '97': 'T19', '96': 'T20', '95':
                          'T19', '94': 'T18', '93': 'T19', '92': 'T20', '91': 'T17', '90': 'T18', '89': 'T19',
                      '88': 'T20', '87': 'T17', '86': 'T18', '85': 'T15', '84': 'T20', '83': 'T17', '82': 'T14',
                      '81': 'T19', '80': 'T20', '79': 'T19', '78': 'T18', '77': 'T19', '76': 'T20', '75': 'T17',
                      '74': 'T14', '73': 'T19', '72': 'T16', '71': 'T13', '70': 'T20', '69': 'T19', '68': 'T18',
                      '67': 'T17', '66': 'T16', '65': 'T15', '64': 'T14', '63': 'T13', '62': 'T12', '61': 'T11',
                      '60': 'S20', '59': 'S19', '58': 'S18', '57': 'S17', '56': 'T16', '55': 'S15', '54': 'S14',
                      '53': 'S13', '52': 'S12', '51': 'S11', '50': 'S10', '49': 'S9', '48': 'S16', '47': 'S7',
                      '46': 'S6', '45': 'S13', '44': 'S12', '43': 'S3', '42': 'S10', '41': 'S9'},

                  3: {'170': 'T20', '167': 'T20', '164': 'T20', '161': 'T20', '160': 'T20', '158': 'T20',
                      '157': 'T20', '156': 'T20', '155': 'T20', '154': 'T20', '153': 'T20', '152': 'T20',
                      '151': 'T20', '150': 'T20', '149': 'T20', '148': 'T20', '147': 'T20', '146': 'T20',
                      '145': 'T20', '144': 'T20', '143': 'T20', '142': 'T20', '141': 'T20', '140': 'T20',
                      '139': 'T20', '138': 'T20', '137': 'T20', '136': 'T20', '135': 'T20', '134': 'T20',
                      '133': 'T20', '132': 'T20', '131': 'T19', '130': 'T20', '129': 'T19', '128': 'T18',
                      '127': 'T20', '126': 'T19', '125': 'T18', '124': 'T20', '123': 'T19', '122': 'T18',
                      '121': 'T20', '120': 'T20', '119': 'T19', '118': 'T20', '117': 'T19', '116': 'T19',
                      '115': 'T20', '114': 'T19', '113': 'T19', '112': 'T20', '111': 'T19', '110': 'T20',
                      '109': 'T20', '108': 'T20',
                      '107': 'T19', '106': 'T20', '105': 'T20', '104': 'T19', '103': 'T19', '102': 'T20',
                      '101': 'T20', '100': 'T20', '99': 'T19', '98': 'T20', '97': 'T19', '96': 'T20', '95':
                          'T19', '94': 'T18', '93': 'T19', '92': 'T20', '91': 'T17', '90': 'T18', '89': 'T19',
                      '88': 'T20', '87': 'T17', '86': 'T18', '85': 'T15', '84': 'T20', '83': 'T17', '82': 'T14',
                      '81': 'T15', '80': 'T20', '79': 'T19', '78': 'T18', '77': 'T19', '76': 'T20', '75': 'T17',
                      '74': 'T14', '73': 'T19', '72': 'T16', '71': 'T13', '70': 'T18', '69': 'T19', '68': 'T16',
                      '67': 'T9', '66': 'T10', '65': 'T11', '64': 'T16', '63': 'T13', '62': 'T10', '61': 'T15',
                      '60': 'S20', '59': 'S19', '58': 'S18', '57': 'S17', '56': 'T16', '55': 'S15', '54': 'S14',
                      '53': 'S13', '52': 'S12', '51': 'S11', '50': 'D25', '49': 'S9', '48': 'S16', '47': 'S7',
                      '46': 'S6', '45': 'S13', '44': 'S12', '43': 'S3', '42': 'S10', '41': 'S9'}
                  }


def get_target(remaining_score, dart, out_mode):
    # valid for the naive checkout table
    if remaining_score > 131:
        return 'T20'

    # master's out currently does not try to check on trebles
    if out_mode == 'do' or 'mo':
        if remaining_score <= 40:
            if remaining_score % 2 == 0:
                return 'D' + str(int(remaining_score / 2))
            else:
                if remaining_score > 32:
                    return 'S' + str(remaining_score - 32)
                elif remaining_score > 16:
                    return 'S' + str(remaining_score - 16)
                elif remaining_score > 8:
                    return 'S' + str(remaining_score - 8)
                elif remaining_score > 4:
                    return 'S' + str(remaining_score - 4)
                else:
                    return 'S' + str(1)
        else:
            return checkout_table[dart][str(remaining_score)]

    # Single Out - just naive checkout attempts
    else:
        if remaining_score > 60:
            return 'T20'
        # always try to checkout on singles if possible
        elif remaining_score < 20 or remaining_score == 25:
            return 'S' + str(remaining_score)
        # try to checkout on doubles if possible
        elif remaining_score % 2 == 0:
            return 'D' + str(int(remaining_score / 2))
        # try to checkout on trebles if possible
        elif remaining_score % 3 == 0:
            return 'T' + str(int(remaining_score / 3))
        # set up 40 if score between 41 and 59
        elif remaining_score > 40:
            return 'S' + str(remaining_score - 40)
        # set up 20 if score between 21 and 39
        else:
            return 'S' + str(remaining_score - 20)


def throw_dart(target, sigma_x, sigma_y):
    # sigma_x = 980
    # sigma_y = 550
    # sigma_x = 1150
    # sigma_y = 650

    if target[0] == 'S':
        distance = 13450
    elif target[0] == 'D':
        distance = 16600
    else:
        distance = 10300

    if target == 'D25' or target == 'S25':
        target_x, target_y = 0, 0
    else:
        dartboard = list([20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5])
        index = dartboard.index(int(target[1:]))
        angle = index * 18

        target_y = distance * cos(radians(angle))
        target_x = sqrt(distance ** 2 - target_y ** 2)
        if index > 10:
            target_x *= -1

    # print('Target: {target} - {x}, {y}'.format(target=target, x=target_x, y=target_y))
    x = np.random.normal(target_x, sigma_x, 1)
    y = np.random.normal(target_y, sigma_y, 1)
    # print(str(x) + ' ' + str(y))
    # plt.plot(x, y, 'bo', markersize=2)
    field = get_field_by_coordinates(x, y)
    # print('Hit: {field}'.format(field=field))

    if field == '0':
        return 0
    elif field[0] == 'S':
        factor = 1
    elif field[0] == 'D':
        factor = 2
    else:
        factor = 3

    number = int(field[1:])
    return number * factor


def get_field_by_coordinates(x, y):
    distance = sqrt((x * x) + (y * y))

    angle = degrees(atan(y / x)) if x != 0 else 0

    double = 17000
    outer_single = 16200
    triple = 10700
    inner_single = 9900
    bull = 1590
    bullseye = 635

    if angle > 0:
        if x > 0:
            quadrant = 'q1'
        else:
            quadrant = 'q3'
    else:
        if x > 0:
            quadrant = 'q2'
        else:
            quadrant = 'q4'

    if abs(angle) <= 9:
        segment = 0
    elif abs(angle) <= 27:
        segment = 1
    elif abs(angle) <= 45:
        segment = 2
    elif abs(angle) <= 63:
        segment = 3
    elif abs(angle) <= 81:
        segment = 4
    else:
        segment = 5

    segments = {
        'q1': [6, 13, 4, 18, 1, 20],
        'q2': [6, 10, 15, 2, 17, 3],
        'q3': [11, 8, 16, 7, 19, 3],
        'q4': [11, 14, 9, 12, 5, 20]
    }

    if distance <= bullseye:
        result = 'D25'
    elif distance <= bull:
        result = 'S25'
    elif distance <= inner_single:
        result = 'S'
    elif distance <= triple:
        result = 'T'
    elif distance <= outer_single:
        result = 'S'
    elif distance <= double:
        result = 'D'
    else:
        result = '0'

    if len(result) == 1 and result != '0':
        result += str(segments[quadrant][segment])

    # print(result)
    return result


def get_computer_score(remaining_score, player, sigma_x, sigma_y):
    # get current remaining score
    thrown_score_total = 0

    for dart in range(1, 4):

        target = get_target(remaining_score, dart, 'do')
        # simulate dart throw
        if target[0] == 'D' and remaining_score <= 50:
            global double_attempts
            double_attempts[player] += 1
        thrown_score = throw_dart(target, sigma_x, sigma_y)
        # if target[0] == 'D' and remaining_score <= 50:
        #   print('Target: {target}, Score: {score}'.format(target=target, score=thrown_score))
        thrown_score_total += thrown_score
        remaining_score -= thrown_score
        # don't keep throwing if leg won or busted
        if remaining_score == 0:
            return thrown_score_total, dart
        elif remaining_score < 0:
            break

    return thrown_score_total, 3


def simulate(sigma_x, sigma_y):
    for i in range(1):
        scores = [[], []]
        legs = [[], []]
        global double_attempts
        nine_darters = [0, 0]
        double_attempts = [0, 0]
        legs_won = [0, 0]
        matches_won = [0, 0]
        averages = [[], []]
        for match in range(20):
            legs_won_match = [0, 0]
            p1_started = True

            while legs_won_match[0] < 6 and legs_won_match[1] < 6:
                remains = [501, 501]
                darts = [0, 0]
                p1_turn = p1_started
                while remains[0] > 0 and remains[1] > 0:
                    p = 0 if p1_turn else 1
                    score, darts_thrown = get_computer_score(remains[p], p, sigma_x, sigma_y)
                    if score <= remains[p]:
                        remains[p] -= score
                        scores[p].append(score)
                    else:
                        scores[p].append(0)
                    darts[p] += darts_thrown

                    p1_turn = not p1_turn

                if remains[0] == 0:
                    legs_won[0] += 1
                    legs_won_match[0] += 1
                else:
                    legs_won[1] += 1
                    legs_won_match[1] += 1

                for p in range(2):
                    legs[p].append(darts[p])

                    if darts[p] == 9 and remains[p] == 0:
                        nine_darters[p] += 1

                p1_started = not p1_started

                time.sleep(0)

            if legs_won_match[0] == 6:
                matches_won[0] += 1
            else:
                matches_won[1] += 1

        return sum(scores[p]) / sum(legs[p]) * 3, legs_won[p] / double_attempts[p]





