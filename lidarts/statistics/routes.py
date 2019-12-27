from lidarts.statistics import bp
from flask_login import current_user, login_required
from flask import render_template
from lidarts.models import User, Game
from sqlalchemy import asc
from lidarts.game.forms import game_types
from datetime import timedelta, datetime
from lidarts.statistics.utils import calculateOverallStatsFromLeg, calculateOverallStatsFromGame, sumUpStats, createStatsObject
from wtforms import Form, RadioField, SelectField
from lidarts.statistics.forms import StatisticsForm

import os
import json

@bp.route('/x01', methods=['GET', 'POST'])
@login_required
def x01():
    form = StatisticsForm()

    stats = {}
    stats['today'] = createStatsObject()
    stats['currentweek'] = createStatsObject()
    stats['currentmonth'] = createStatsObject()
    stats['currentyear'] = createStatsObject()
    stats['overall'] = createStatsObject()
    stats['custom'] = createStatsObject()
    stats['averagepergame'] = []

    user = User.query.filter(User.id == current_user.id).first_or_404()

    #if (form.is_submitted):
    customFilterNumberOfGames = form.numberOfGames.default
    customFilterDateFrom = form.dateFrom.default
    customFilterDateTo = form.dateTo.default

    # if no value is in the form data, we can insert the default values
    if (form.numberOfGames.data == None):
        form.numberOfGames.data = customFilterNumberOfGames
    if (form.dateFrom.data == None):
        form.dateFrom.data = customFilterDateFrom
    if (form.dateTo.data == None):
        form.dateTo.data = customFilterDateTo

    # check which custom filter is active
    useCustomFilterLastGames = False
    useCustomFilterDateRange = False
    if (form.selectGameRangeFilter.data == 'lastgames'):
        useCustomFilterLastGames = True
        customFilterNumberOfGames = form.numberOfGames.data
    elif (form.selectGameRangeFilter.data == 'daterange'):
        useCustomFilterDateRange = True
        customFilterDateFrom = form.dateFrom.data
        customFilterDateTo = form.dateTo.data
    else:
        useCustomFilterLastGames = True

    #TODO: Check Performance select with Game.begin vs. Game.id
    games = Game.query.filter(((Game.player1 == user.id) | (Game.player2 == user.id)) & (Game.status != 'challenged')
                            & (Game.status != 'declined') & (Game.status != 'aborted')) \
        .order_by(asc(Game.begin)).all()

    # get the dates for date related statistics
    todayDate = datetime.today().date()
    startCurrentWeek = todayDate - timedelta(days=todayDate.weekday())
    startCurrentMonth = todayDate.replace(day = 1)

    number_of_games = 0
    # iterate through each game
    for game in games:
        gameBeginDate = game.begin.date()

        player = '1' 
        if not(user.id == game.player1):
            '2'

        number_of_games += 1

        # check if game is valid for the current custom filter settings
        validGameForCustomFilter = False
        if (useCustomFilterLastGames and number_of_games <= customFilterNumberOfGames):
            validGameForCustomFilter = True
        elif (useCustomFilterDateRange and gameBeginDate >= customFilterDateFrom and gameBeginDate <= customFilterDateTo):
            validGameForCustomFilter = True

        # custom filter
        if (validGameForCustomFilter):
            calculateOverallStatsFromGame(stats['custom'], game)

        # use for today statistics?
        if (gameBeginDate == todayDate):
            calculateOverallStatsFromGame(stats['today'], game)

        # use current week statistics?
        if (gameBeginDate >= startCurrentWeek):
            calculateOverallStatsFromGame(stats['currentweek'], game)

        # use current month statistics?
        if (gameBeginDate >= startCurrentMonth):
            calculateOverallStatsFromGame(stats['currentmonth'], game)

        # use current year statistics?
        if (gameBeginDate.year >= todayDate.year):
            calculateOverallStatsFromGame(stats['currentyear'], game)

        # overall stats
        calculateOverallStatsFromGame(stats['overall'], game)

        match_json = json.loads(game.match_json)

        # calculate current game stats
        currentGameStats = {'darts_thrown': 0, 'total_score': 0}

        # iterate through each set/leg
        for set in match_json:
            for leg in match_json[set]:
                currentPlayerLegStats = match_json[set][leg][player]

                # add stats for current game
                currentGameStats['darts_thrown'] += len(currentPlayerLegStats['scores']) * 3
                currentGameStats['total_score'] += sum(currentPlayerLegStats['scores'])
                if 'to_finish' in currentPlayerLegStats:
                    currentGameStats['darts_thrown'] -= (3 - currentPlayerLegStats['to_finish'])

                # custom filter
                if (validGameForCustomFilter):
                    calculateOverallStatsFromLeg(stats['custom'], currentPlayerLegStats)

                # use for today statistics?
                if (gameBeginDate == todayDate):
                    calculateOverallStatsFromLeg(stats['today'], currentPlayerLegStats)

                # use current week statistics?
                if (gameBeginDate >= startCurrentWeek):
                    calculateOverallStatsFromLeg(stats['currentweek'], currentPlayerLegStats)

                # use current month statistics?
                if (gameBeginDate >= startCurrentMonth):
                    calculateOverallStatsFromLeg(stats['currentmonth'], currentPlayerLegStats)

                # use current year statistics?
                if (gameBeginDate.year >= todayDate.year):
                    calculateOverallStatsFromLeg(stats['currentyear'], currentPlayerLegStats)

                # overall stats
                calculateOverallStatsFromLeg(stats['overall'], currentPlayerLegStats)

        # sum up average per game stats
        gameAverage = round((currentGameStats['total_score'] / (currentGameStats['darts_thrown'])) * 3, 2)
        stats['averagepergame'].append(gameAverage)

    # sum up all the stats
    sumUpStats(stats['custom'])
    sumUpStats(stats['today'])
    sumUpStats(stats['currentweek'])
    sumUpStats(stats['currentmonth'])
    sumUpStats(stats['currentyear'])
    sumUpStats(stats['overall'])

    activeNavPage = ''
    # if we are in post (from filter), we must append the prefix for the internal link
    if (form.is_submitted()):
       activeNavPage = 'custom'

    return render_template('statistics/x01.html', stats = stats, form = form, activeNavPage = activeNavPage)