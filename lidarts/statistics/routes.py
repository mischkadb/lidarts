from lidarts.statistics import bp
from flask_login import current_user, login_required
from flask import render_template
from lidarts.models import User, Game
from sqlalchemy import desc
from lidarts.game.forms import game_types
from datetime import datetime, timedelta
from lidarts.statistics.utils import calculateOverallStatsFromLeg, sumUpStats, createStatsObject

import os
import json

@bp.route('/x01')
@login_required
def x01():
    stats = {}
    stats['today'] = createStatsObject()
    stats['currentweek'] = createStatsObject()
    stats['currentmonth'] = createStatsObject()
    stats['averagepergame'] = []

    user = User.query.filter(User.id == current_user.id).first_or_404()
    
    #TODO: check if game_types array can be used in query?
    games = Game.query.filter(((Game.player1 == user.id) | (Game.player2 == user.id)) & (Game.status != 'challenged')
                              & (Game.status != 'declined') & (Game.status != 'aborted')) \
        .order_by(desc(Game.id)).all()

    todayDate = datetime.today().date()

    startCurrentWeek = todayDate - timedelta(days=todayDate.weekday())

    startCurrentMonth = todayDate
    if startCurrentMonth.day > 25:
        startCurrentMonth += datetime.timedelta(7)
    startCurrentMonth = startCurrentMonth.replace(day=1)

    for game in games:
        player = '1' 
        if not(user.id == game.player1):
            '2'

        match_json = json.loads(game.match_json)
        for set in match_json:
            for leg in match_json[set]:
                gameBeginDate = game.begin.date()

                currentPlayerLegStats = match_json[set][leg][player]

                # calculate current game stats
                currentGameStats = {'darts_thrown': 0, 'total_score': 0}
                
                currentGameStats['darts_thrown'] += len(currentPlayerLegStats['scores']) * 3
                currentGameStats['total_score'] += sum(currentPlayerLegStats['scores'])
                if 'to_finish' in currentPlayerLegStats:
                    currentGameStats['darts_thrown'] -= (3 - currentPlayerLegStats['to_finish'])
                
                gameAverage = round((currentGameStats['total_score'] / (currentGameStats['darts_thrown'])) * 3, 2)

                stats['averagepergame'].append(gameAverage)

                # use for today statistics?
                if (gameBeginDate == todayDate):
                    calculateOverallStatsFromLeg(stats['today'], currentPlayerLegStats)

                # use current week statistics?
                if (gameBeginDate >= startCurrentWeek):
                    calculateOverallStatsFromLeg(stats['currentweek'], currentPlayerLegStats)

                # use current month statistics?
                if (gameBeginDate >= startCurrentMonth):
                    calculateOverallStatsFromLeg(stats['currentmonth'], currentPlayerLegStats)

    # sum up all the stats
    sumUpStats(stats['today'])
    sumUpStats(stats['currentweek'])
    sumUpStats(stats['currentmonth'])

    return render_template('statistics/x01.html', stats = stats)