from flask_babelex import lazy_gettext
from lidarts.models import User
from collections import defaultdict


def get_player_names(game):
    if game.player1:
        player_one_name = get_name_by_id(game.player1)

    if game.opponent_type == 'local':
        player_two_name = lazy_gettext('Local Guest')
    elif game.opponent_type == 'online':
        player_two_name = get_name_by_id(game.player2)
    else:
        game_dict = game.__dict__

        # computer game
        player_two_name = 'Trainer ' + game_dict['opponent_type'][8:]

    return player_one_name, player_two_name


def get_name_by_id(id_):
    if id_ is None:
        return lazy_gettext('Guest')
    user = User.query.get(id_)
    if user:
        return user.username
    else:
        return None


def collect_statistics_cricket(game, match_json):
    stats = {}

    p1_marks = 0
    p2_marks = 0
    p1_rounds = 0
    p2_rounds = 0
    p1_mpr_distribution = defaultdict(int)
    p2_mpr_distribution = defaultdict(int)
    leg_overview = {}

    for set_ in match_json:
        leg_overview[set_] = {}
        for leg in match_json[set_]:
            leg_overview[set_][leg] = {'mpr': {}}
            p1_rounds += len(match_json[set_][leg]['1']['scores'])
            p2_rounds += len(match_json[set_][leg]['2']['scores'])
            p1_marks_in_leg = 0
            p2_marks_in_leg = 0
            for scores in match_json[set_][leg]['1']['scores']:
                marks_in_round = 0
                for score in scores:
                    if score == 0:
                        marks = 0
                    elif 0 < score <= 25:
                        marks = 1
                    elif 25 < score <= 40 or score == 50:
                        marks = 2
                    else:
                        marks = 3

                    marks_in_round += marks

                p1_marks_in_leg += marks_in_round                    
                p1_mpr_distribution[marks_in_round] += 1

            for scores in match_json[set_][leg]['2']['scores']:
                marks_in_round = 0
                for score in scores:
                    if score == 0:
                        marks = 0
                    elif 0 < score <= 25:
                        marks = 1
                    elif 25 < score <= 40 or score == 50:
                        marks = 2
                    else:
                        marks = 3

                    marks_in_round += marks

                p2_marks_in_leg += marks_in_round                    
                p2_mpr_distribution[marks_in_round] += 1

            leg_overview[set_][leg]['mpr']['1'] = p1_marks_in_leg / len(match_json[set_][leg]['1']['scores']) if len(match_json[set_][leg]['1']['scores']) else 0
            leg_overview[set_][leg]['mpr']['2'] = p2_marks_in_leg / len(match_json[set_][leg]['2']['scores']) if len(match_json[set_][leg]['2']['scores']) else 0
            p1_all_marks_open = all(field['marks'] == 3 for field in match_json[set_][leg]['1']['fields'].values())
            if (
                (match_json[set_][leg]['1']['points'] > match_json[set_][leg]['2']['points']) 
                or (match_json[set_][leg]['1']['points'] == match_json[set_][leg]['2']['points'] and p1_all_marks_open)
            ):
                leg_overview[set_][leg]['winner'] = '1'
            else:
                leg_overview[set_][leg]['winner'] = '2'
            p1_marks += p1_marks_in_leg
            p2_marks += p2_marks_in_leg

    stats['p1_mpr'] = round(p1_marks / p1_rounds, 2) if p1_rounds else 0
    stats['p2_mpr'] = round(p2_marks / p2_rounds, 2) if p2_rounds else 0
    stats['p1_mpr_distribution'] = p1_mpr_distribution
    stats['p2_mpr_distribution'] = p2_mpr_distribution
    stats['p1_rounds'] = p1_rounds
    stats['p2_rounds'] = p2_rounds
    stats['leg_overview'] = leg_overview

    return stats


def collect_statistics(game, match_json):
    if game.variant == 'cricket':
        return collect_statistics_cricket(game, match_json)

    stats = defaultdict(int)
    scores = ([], [])
    first9_scores = ([], [])
    short_leg = [0, 0]
    short_legs = ([], [])
    high_finish = [0, 0]
    high_finishes = ([], [])

    darts_thrown = [0, 0]
    darts_thrown_double = [0, 0]
    legs_won = [0, 0]

    for set_ in match_json:
        for leg in match_json[set_]:
            if isinstance(match_json[set_][leg]['1']['double_missed'], (list,)):
                darts_thrown_double[0] += sum(match_json[set_][leg]['1']['double_missed'])
                darts_thrown_double[1] += sum(match_json[set_][leg]['2']['double_missed'])
            else:
                # legacy: double_missed as int
                darts_thrown_double[0] += match_json[set_][leg]['1']['double_missed']
                darts_thrown_double[1] += match_json[set_][leg]['2']['double_missed']

            darts_thrown_this_leg = [
                len(match_json[set_][leg]['1']['scores']) * 3,
                len(match_json[set_][leg]['2']['scores']) * 3,
            ]

            player = 0 if sum(match_json[set_][leg]['1']['scores']) == game.type else 1
            player_string = '1' if player == 0 else '2'
                
            if 'to_finish' in match_json[set_][leg][player_string]:
                darts_thrown_this_leg[player] -= (3 - match_json[set_][leg][player_string]['to_finish'])

            darts_thrown_double[player] += 1
            legs_won[player] += 1

            short_leg[player] = darts_thrown_this_leg[player] \
                if short_leg[player] == 0 else short_leg[player]
            short_leg[player] = min(darts_thrown_this_leg[player], short_leg[player])
            if darts_thrown_this_leg[player] <= 18:
                short_legs[player].append(darts_thrown_this_leg[player])
            finish_score = match_json[set_][leg][player_string]['scores'][-1]
            high_finish[player] = max(finish_score, high_finish[player])
            if finish_score > 100:
                high_finishes[player].append(finish_score)               

            darts_thrown[0] += darts_thrown_this_leg[0]
            darts_thrown[1] += darts_thrown_this_leg[1]

            for player in (0, 1):
                player_string = '1' if player == 0 else '2'
                for i, score in enumerate(match_json[set_][leg][player_string]['scores']):
                    scores[player].append(score)
                    if i <= 2:
                        first9_scores[player].append(score)
                    if score == 180:
                        stats[f'p{player_string}_180'] += 1
                    elif score >= 171:
                        stats[f'p{player_string}_171'] += 1
                    elif score >= 140:
                        stats[f'p{player_string}_140'] += 1
                    elif score >= 100:
                        stats[f'p{player_string}_100'] += 1
                    elif score >= 80:
                        stats[f'p{player_string}_80'] += 1
                    elif score >= 60:
                        stats[f'p{player_string}_60'] += 1
                    elif score >= 40:
                        stats[f'p{player_string}_40'] += 1
                    elif score >= 20:
                        stats[f'p{player_string}_20'] += 1
                    else:
                        stats[f'p{player_string}_0'] += 1

                stats[f'p{player_string}_match_avg'] = round(sum(scores[player]) / (darts_thrown[player] / 3), 2) if scores[player] else 0
                stats[f'p{player_string}_first9_avg'] = round(sum(first9_scores[player])/len(first9_scores[player]), 2) if first9_scores[player] else 0
                stats[f'p{player_string}_doubles'] = int(legs_won[player] / darts_thrown_double[player] * 10000) / 100 if legs_won[player] else 0
                stats[f'p{player_string}_legs_won'] = legs_won[player]
                stats[f'p{player_string}_darts_thrown_double'] = darts_thrown_double[player]
                stats[f'p{player_string}_short_leg'] = short_leg[player]                
                stats[f'p{player_string}_short_legs'] = sorted(short_legs[player])
                stats[f'p{player_string}_high_finish'] = high_finish[player]
                stats[f'p{player_string}_high_finishes'] = sorted(high_finishes[player], reverse=True)
    return stats

cricket_leg_default = {
    1: {
        'scores': [],
        'points': 0,
        'fields': {
            15: {
                'marks': 0,
                'score': 0,
            },
            16: {
                'marks': 0,
                'score': 0,
            },
            17: {
                'marks': 0,
                'score': 0,
            },
            18: {
                'marks': 0,
                'score': 0,
            },
            19: {
                'marks': 0,
                'score': 0,
            },
            20: {
                'marks': 0,
                'score': 0,
            },
            25: {
                'marks': 0,
                'score': 0,
            },
        }
    },
    2: {
        'scores': [],
        'points': 0,
        'fields': {
            15: {
                'marks': 0,
                'score': 0,
            },
            16: {
                'marks': 0,
                'score': 0,
            },
            17: {
                'marks': 0,
                'score': 0,
            },
            18: {
                'marks': 0,
                'score': 0,
            },
            19: {
                'marks': 0,
                'score': 0,
            },
            20: {
                'marks': 0,
                'score': 0,
            },
            25: {
                'marks': 0,
                'score': 0,
            },
        },
    },
}