from flask_babelex import lazy_gettext
from lidarts.models import User, UserSettings
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

def get_player_countries(game):
    if game.player1:
        player_one_country = get_country_by_id(game.player1)

    if game.opponent_type == 'local':
        player_one_country = None
    elif game.opponent_type == 'online':
        player_two_country = get_country_by_id(game.player2)

    return player_one_country, player_two_country

def get_country_by_id(id_):
    if id_ is None:
        return None
    country = UserSettings.query.with_entities(UserSettings.country).filter_by(user=id_).first()
    if country:
        country = country[0]
        return country


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

    for set_ in match_json:
        for leg in match_json[set_]:
            if isinstance(match_json[set_][leg]['1']['double_missed'], (list,)):
                p1_darts_thrown_double += sum(match_json[set_][leg]['1']['double_missed'])
                p2_darts_thrown_double += sum(match_json[set_][leg]['2']['double_missed'])
            else:
                # legacy: double_missed as int
                p1_darts_thrown_double += match_json[set_][leg]['1']['double_missed']
                p2_darts_thrown_double += match_json[set_][leg]['2']['double_missed']

            p1_darts_thrown_this_leg = len(match_json[set_][leg]['1']['scores']) * 3
            p2_darts_thrown_this_leg = len(match_json[set_][leg]['2']['scores']) * 3

            if sum(match_json[set_][leg]['1']['scores']) == game.type:
                if 'to_finish' in match_json[set_][leg]['1']:
                    p1_darts_thrown_this_leg -= (3 - match_json[set_][leg]['1']['to_finish'])

                p1_darts_thrown_double += 1
                p1_legs_won += 1

                stats['p1_short_leg'] = p1_darts_thrown_this_leg \
                    if stats['p1_short_leg'] == 0 else stats['p1_short_leg']
                stats['p1_short_leg'] = p1_darts_thrown_this_leg \
                    if p1_darts_thrown_this_leg < stats['p1_short_leg'] else stats['p1_short_leg']
                stats['p1_high_finish'] = match_json[set_][leg]['1']['scores'][-1] \
                    if match_json[set_][leg]['1']['scores'][-1] > stats['p1_high_finish'] else stats['p1_high_finish']

            if sum(match_json[set_][leg]['2']['scores']) == game.type:
                if 'to_finish' in match_json[set_][leg]['2']:
                    p2_darts_thrown_this_leg -= (3 - match_json[set_][leg]['2']['to_finish'])

                p2_darts_thrown_double += 1
                p2_legs_won += 1

                stats['p2_short_leg'] = p2_darts_thrown_this_leg \
                    if stats['p2_short_leg'] == 0 else stats['p2_short_leg']
                stats['p2_short_leg'] = p2_darts_thrown_this_leg \
                    if p2_darts_thrown_this_leg < stats['p2_short_leg'] else stats['p2_short_leg']
                stats['p2_high_finish'] = match_json[set_][leg]['2']['scores'][-1] \
                    if match_json[set_][leg]['2']['scores'][-1] > stats['p2_high_finish'] else stats['p2_high_finish']

            p1_darts_thrown += p1_darts_thrown_this_leg
            p2_darts_thrown += p2_darts_thrown_this_leg

            for i, score in enumerate(match_json[set_][leg]['1']['scores']):
                p1_scores.append(score)
                if i <= 2:
                    p1_first9_scores.append(score)
                if score == 180:
                    stats['p1_180'] += 1
                elif score >= 171:
                    stats['p1_171'] += 1
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

            for i, score in enumerate(match_json[set_][leg]['2']['scores']):
                p2_scores.append(score)
                if i <= 2:
                    p2_first9_scores.append(score)
                if score == 180:
                    stats['p2_180'] += 1
                elif score >= 171:
                    stats['p2_171'] += 1
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