from lidarts import db
from lidarts.models import User
from collections import defaultdict


def get_name_by_id(id):
    if id is None:
        return 'Guest'
    user = User.query.get(id)
    if user:
        return user.username
    else:
        return None


def collect_statistics(game, match_json):

    stats = defaultdict(int)
    p1_scores = []
    p2_scores = []
    p1_first9_scores = []
    p2_first9_scores = []
    stats['p1_short_leg'] = 0
    stats['p2_short_leg'] = 0

    p1_darts_thrown = 0
    p1_darts_thrown_double = 0
    p1_legs_won = 0
    p2_darts_thrown = 0
    p2_darts_thrown_double = 0
    p2_legs_won = 0

    for set in match_json:
        for leg in match_json[set]:
            if isinstance(match_json[set][leg]['1']['double_missed'], (list,)):
                p1_darts_thrown_double += sum(match_json[set][leg]['1']['double_missed'])
                p2_darts_thrown_double += sum(match_json[set][leg]['2']['double_missed'])
            else:
                # legacy: double_missed as int
                p1_darts_thrown_double += match_json[set][leg]['1']['double_missed']
                p2_darts_thrown_double += match_json[set][leg]['2']['double_missed']

            p1_darts_thrown_this_leg = len(match_json[set][leg]['1']['scores']) * 3
            p2_darts_thrown_this_leg = len(match_json[set][leg]['2']['scores']) * 3

            if sum(match_json[set][leg]['1']['scores']) == game.type:
                if 'to_finish' in match_json[set][leg]['1']:
                    p1_darts_thrown_this_leg -= (3 - match_json[set][leg]['1']['to_finish'])

                p1_darts_thrown_double += 1
                p1_legs_won += 1

                stats['p1_short_leg'] = p1_darts_thrown_this_leg \
                    if stats['p1_short_leg'] == 0 else stats['p1_short_leg']
                stats['p1_short_leg'] = p1_darts_thrown_this_leg \
                    if p1_darts_thrown_this_leg < stats['p1_short_leg'] else stats['p1_short_leg']
                stats['p1_high_finish'] = match_json[set][leg]['1']['scores'][-1] \
                    if match_json[set][leg]['1']['scores'][-1] > stats['p1_high_finish'] else stats['p1_high_finish']

            if sum(match_json[set][leg]['2']['scores']) == game.type:
                if 'to_finish' in match_json[set][leg]['2']:
                    p2_darts_thrown_this_leg -= (3 - match_json[set][leg]['2']['to_finish'])

                p2_darts_thrown_double += 1
                p2_legs_won += 1

                stats['p2_short_leg'] = p2_darts_thrown_this_leg \
                    if stats['p2_short_leg'] == 0 else stats['p2_short_leg']
                stats['p2_short_leg'] = p2_darts_thrown_this_leg \
                    if p2_darts_thrown_this_leg < stats['p2_short_leg'] else stats['p2_short_leg']
                stats['p2_high_finish'] = match_json[set][leg]['2']['scores'][-1] \
                    if match_json[set][leg]['2']['scores'][-1] > stats['p2_high_finish'] else stats['p2_high_finish']

            p1_darts_thrown += p1_darts_thrown_this_leg
            p2_darts_thrown += p2_darts_thrown_this_leg

            for i, score in enumerate(match_json[set][leg]['1']['scores']):
                p1_scores.append(score)
                if i <= 3:
                    p1_first9_scores.append(score)
                if score == 180:
                    stats['p1_180'] += 1
                elif score >= 140:
                    stats['p1_140'] += 1
                elif score >= 100:
                    stats['p1_100'] += 1
                elif score >= 80:
                    stats['p1_80'] += 1
                elif score >= 60:
                    stats['p1_60'] += 1
                elif score >= 40:
                    stats['p1_40'] += 1
                elif score >= 20:
                    stats['p1_20'] += 1
                else:
                    stats['p1_0'] += 1

            for i, score in enumerate(match_json[set][leg]['2']['scores']):
                p2_scores.append(score)
                if i <= 3:
                    p2_first9_scores.append(score)
                if score == 180:
                    stats['p2_180'] += 1
                elif score >= 140:
                    stats['p2_140'] += 1
                elif score >= 100:
                    stats['p2_100'] += 1
                elif score >= 80:
                    stats['p2_80'] += 1
                elif score >= 60:
                    stats['p2_60'] += 1
                elif score >= 40:
                    stats['p2_40'] += 1
                elif score >= 20:
                    stats['p2_20'] += 1
                else:
                    stats['p2_0'] += 1

    stats['p1_match_avg'] = round(sum(p1_scores) / (p1_darts_thrown / 3), 2) if p1_scores else 0
    stats['p2_match_avg'] = round(sum(p2_scores) / (p2_darts_thrown / 3), 2) if p2_scores else 0
    stats['p1_first9_avg'] = round(sum(p1_first9_scores)/len(p1_first9_scores), 2) if p1_first9_scores else 0
    stats['p2_first9_avg'] = round(sum(p2_first9_scores)/len(p2_first9_scores), 2) if p2_first9_scores else 0

    stats['p1_doubles'] = int(p1_legs_won / p1_darts_thrown_double * 10000) / 100 if p1_legs_won else 0
    stats['p2_doubles'] = int(p2_legs_won / p2_darts_thrown_double * 10000) / 100 if p2_legs_won else 0

    stats['p1_legs_won'] = p1_legs_won
    stats['p2_legs_won'] = p2_legs_won

    stats['p1_darts_thrown_double'] = p1_darts_thrown_double
    stats['p2_darts_thrown_double'] = p2_darts_thrown_double

    return stats
