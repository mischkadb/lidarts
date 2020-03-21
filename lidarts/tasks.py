from lidarts import create_app
from lidarts import db
from lidarts.models import Game, UserStatistic
import json
from sqlalchemy import or_

app = create_app()
app.app_context().push()


def calc_cached_stats(player_id):
    games = (
        Game.query
        .filter(
            or_(Game.player1 == player_id, Game.player2 == player_id) 
            & (Game.status == 'completed')
            & (Game.type == '501')
            & (Game.in_mode == 'si')
            & (Game.out_mode == 'do')
        )
        .order_by(Game.id.desc())
        .limit(20).all()
    )
    total_score = 0
    darts_thrown = 0
    legs_won = 0
    double_missed = 0
    for game in games:
        if darts_thrown > 5000:
            break
        player = '1' if game.player1 == player_id else '2'
        match_json = json.loads(game.match_json)
        for set_ in match_json:
            if darts_thrown > 5000:
                break
            for leg in match_json[set_]:
                if darts_thrown > 5000:
                    break
                current_leg = match_json[set_][leg][player]
                total_score += sum(current_leg['scores']) 
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

    user_statistic = UserStatistic.query.filter_by(user=player_id).first()
    if not user_statistic:
        user_statistic = UserStatistic(user=player_id, average=average, doubles=doubles)
        db.session.add(user_statistic)
    else:
        user_statistic.average = average
        user_statistic.doubles = doubles
    db.session.commit()
