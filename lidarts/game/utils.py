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

    for set in match_json:
        for leg in match_json[set]:
            if sum(match_json[set][leg]['1']) == game.type:
                stats['p1_short_leg'] = len(match_json[set][leg]['1'])*3 \
                    if len(match_json[set][leg]['1']) < stats['p1_short_leg'] or stats['p1_short_leg'] == 0\
                    else stats['p1_short_leg']
                stats['p1_high_finish'] = match_json[set][leg]['1'][-1] \
                    if match_json[set][leg]['1'][-1] > stats['p1_high_finish'] else stats['p1_high_finish']

            if sum(match_json[set][leg]['2']) == game.type:
                stats['p2_short_leg'] = len(match_json[set][leg]['2'])*3 \
                    if len(match_json[set][leg]['2']) < stats['p2_short_leg'] or stats['p2_short_leg'] == 0\
                    else stats['p2_short_leg']
                stats['p2_high_finish'] = match_json[set][leg]['2'][-1] \
                    if match_json[set][leg]['2'][-1] > stats['p2_high_finish'] else stats['p2_high_finish']

            for i, score in enumerate(match_json[set][leg]['1']):
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
                    stats['p1_800'] += 1
                elif score >= 60:
                    stats['p1_60'] += 1
                elif score >= 40:
                    stats['p1_40'] += 1
                elif score >= 20:
                    stats['p1_20'] += 1
                else:
                    stats['p1_0'] += 1

            for i, score in enumerate(match_json[set][leg]['2']):
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
                    stats['p2_800'] += 1
                elif score >= 60:
                    stats['p2_60'] += 1
                elif score >= 40:
                    stats['p2_40'] += 1
                elif score >= 20:
                    stats['p2_20'] += 1
                else:
                    stats['p2_0'] += 1

    stats['p1_match_avg'] = round(sum(p1_scores) / len(p1_scores), 2) if p1_scores else 0
    stats['p2_match_avg'] = round(sum(p2_scores) / len(p2_scores), 2) if p2_scores else 0
    stats['p1_first9_avg'] = round(sum(p1_first9_scores)/len(p1_first9_scores), 2) if p1_first9_scores else 0
    stats['p2_first9_avg'] = round(sum(p2_first9_scores)/len(p2_first9_scores), 2) if p2_first9_scores else 0

    return stats
