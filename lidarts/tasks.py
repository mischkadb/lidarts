from lidarts import create_app
from lidarts import db, mail, socketio
from lidarts.models import Game, User, UserStatistic
import json
from sqlalchemy import or_
from sqlalchemy.orm import aliased
from datetime import datetime
import time
import logging

app = create_app()
app.app_context().push()


def calc_stats(player_id, max_games=None, max_darts=None):
    player1_stats = aliased(UserStatistic)
    player2_stats = aliased(UserStatistic)
    games_query = (
        Game.query
        .join(player1_stats, Game.player1 == player1_stats.user, isouter=True).add_columns(player1_stats.average)
        .join(player2_stats, Game.player2 == player2_stats.user, isouter=True).add_columns(player2_stats.average)
        .filter(
            or_(Game.player1 == player_id, Game.player2 == player_id)
            & (Game.status == 'completed')
            & (Game.type == '501')
            & (Game.in_mode == 'si')
            & (Game.out_mode == 'do')
        )
        .order_by(Game.id.desc())
    )

    if max_games:
        games_query = games_query.limit(max_games)

    games = games_query.all()

    match_stats = {
        'matches': {
            0: 0,
            30: 0,
            40: 0,
            50: 0,
            60: 0,
            70: 0,
            80: 0,
            90: 0,
        },
        'wins': {
            0: 0,
            30: 0,
            40: 0,
            50: 0,
            60: 0,
            70: 0,
            80: 0,
            90: 0,
        },
    }
    total_score = 0
    total_score_first9 = 0
    darts_thrown = 0
    legs_played = 0
    legs_won = 0
    double_missed = 0
    for game, p1_average, p2_average in games:
        if max_darts and darts_thrown > max_darts:
            break
        player = '1' if game.player1 == player_id else '2'

        o_average = 0
        p_won = False
        if game.player2 and (game.player1 == player_id and game.player2 != player_id):
            o_average = p2_average
            p_won = game.p1_sets > game.p2_sets
        elif game.player2 and (game.player2 == player_id and game.player1 != player_id):
            o_average = p1_average
            p_won = game.p1_sets < game.p2_sets

        if o_average:
            average_bin = round(o_average - 5.1, -1)
            average_bin = 0 if average_bin < 30 else average_bin
            average_bin = 90 if average_bin > 90 else average_bin
            match_stats['matches'][average_bin] += 1
            if p_won:
                match_stats['wins'][average_bin] += 1

        match_json = json.loads(game.match_json)
        for set_ in match_json:
            socketio.sleep(0)
            if max_darts and darts_thrown > max_darts:
                break
            for leg in match_json[set_]:
                legs_played += 1
                if max_darts and darts_thrown > max_darts:
                    break
                current_leg = match_json[set_][leg][player]
                total_score += sum(current_leg['scores'])
                first9_score = sum(current_leg['scores'][:3]) if len(current_leg['scores']) > 2 else sum(current_leg['scores'][:2])
                total_score_first9 += first9_score
                to_finish = (3 - current_leg['to_finish']) if 'to_finish' in current_leg else 0                
                darts_thrown += len(current_leg['scores']) * 3 - to_finish
                legs_won = legs_won + 1 if sum(current_leg['scores']) == 501 else legs_won
                if isinstance(current_leg['double_missed'], (list,)):
                    double_missed += sum(current_leg['double_missed'])
                else:
                    # legacy: double_missed as int
                    double_missed += current_leg['double_missed']
    average = round((total_score / darts_thrown) * 3, 1) if darts_thrown != 0 else 0
    doubles = round(((legs_won / (legs_won + double_missed)) * 100), 1) if legs_won + double_missed != 0 else 0
    first9 = round((total_score_first9 / legs_played) / 3, 1) if darts_thrown != 0 else 0

    return average, doubles, first9, darts_thrown, len(games), match_stats


def calc_cached_stats(player_id):
    # recent average and doubles for chat and profile
    average, doubles, first9, _, _, _ = calc_stats(player_id, max_games=20, max_darts=5000)
    total_average, total_doubles, total_first9, darts_thrown, total_games, match_stats = calc_stats(player_id)

    user_statistic = UserStatistic.query.filter_by(user=player_id).first()
    if not user_statistic:
        user_statistic = UserStatistic(
            user=player_id,
            average=average,
            doubles=doubles,
            first9=first9,
            darts_thrown=darts_thrown,
            total_games=total_games,
            matches_u30=match_stats['matches'][0],
            matches30_40=match_stats['matches'][30],
            matches40_50=match_stats['matches'][40],
            matches50_60=match_stats['matches'][50],
            matches60_70=match_stats['matches'][60],
            matches70_80=match_stats['matches'][70],
            matches80_90=match_stats['matches'][80],
            matches_o90=match_stats['matches'][90],
            wins_u30=match_stats['wins'][0],
            wins30_40=match_stats['wins'][30],
            wins40_50=match_stats['wins'][40],
            wins50_60=match_stats['wins'][50],
            wins60_70=match_stats['wins'][60],
            wins70_80=match_stats['wins'][70],
            wins80_90=match_stats['wins'][80],
            wins_o90=match_stats['wins'][90],
        )
        db.session.add(user_statistic)
    else:
        user_statistic.average = average
        user_statistic.doubles = doubles
        user_statistic.first9 = first9
        user_statistic.darts_thrown = darts_thrown
        user_statistic.total_games = total_games
        user_statistic.matches_u30 = match_stats['matches'][0]
        user_statistic.matches30_40 = match_stats['matches'][30]
        user_statistic.matches40_50 = match_stats['matches'][40]
        user_statistic.matches50_60 = match_stats['matches'][50]
        user_statistic.matches60_70 = match_stats['matches'][60]
        user_statistic.matches70_80 = match_stats['matches'][70]
        user_statistic.matches80_90 = match_stats['matches'][80]
        user_statistic.matches_o90 = match_stats['matches'][90]
        user_statistic.wins_u30 = match_stats['wins'][0]
        user_statistic.wins30_40 = match_stats['wins'][30]
        user_statistic.wins40_50 = match_stats['wins'][40]
        user_statistic.wins50_60 = match_stats['wins'][50]
        user_statistic.wins60_70 = match_stats['wins'][60]
        user_statistic.wins70_80 = match_stats['wins'][70]
        user_statistic.wins80_90 = match_stats['wins'][80]
        user_statistic.wins_o90 = match_stats['wins'][90]
    db.session.commit()


def bulk_update_last_seen():
    start_time = time.perf_counter()
    #mappings = []
    timestamp = datetime.utcnow()
    while True:
        user_id = app.redis.spop('last_seen_bulk_user_ids')
        if not user_id:
            break
        user = User.query.filter_by(id=int(user_id)).update({'last_seen': timestamp})
        socketio.sleep(0)

    while True:
        user_id = app.redis.spop('last_seen_ingame_bulk_user_ids')
        if not user_id:
            break
        user = User.query.filter_by(id=int(user_id)).update({'last_seen_ingame': timestamp})
        socketio.sleep(0)
        #mappings.append({'id': int(user_id), 'last_seen': timestamp})
    #db.session.bulk_update_mappings(User, mappings)
    db.session.commit()
    logging.info(time.perf_counter() - start_time)


def send_mail(msg):
    mail.send(msg)
