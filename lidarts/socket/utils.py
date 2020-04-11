from flask import request
from flask_socketio import emit
from flask_login import current_user
from lidarts import db, avatars, socketio
from lidarts.models import Game, Tournament, User, UserSettings, UserStatistic, WebcamSettings
import math
import json
from datetime import datetime, timedelta
from sqlalchemy import or_


def player1_started_leg(leg):
    # player 1 started leg if player 1 threw more darts (no break)
    # or player 1 lost the leg and threw the same amount of darts (break)
    return len(leg['1']['scores']) > len(leg['2']['scores']) \
           or (len(leg['1']['scores']) == len(leg['2']['scores'])
               and sum(leg['1']['scores']) < sum(leg['2']['scores']))


def player_to_dict(game, player1):
    player_dict = {
        'bo_legs': game.bo_legs,
        'bo_sets': game.bo_sets,
        'two_clear_legs': game.two_clear_legs,
        'type': game.type,
        'status': game.status
    }
    if player1:
        player_dict['p_score'] = game.p1_score
        player_dict['p_legs'] = game.p1_legs
        player_dict['p_sets'] = game.p1_sets
        player_dict['o_legs'] = game.p2_legs
        player_dict['o_sets'] = game.p2_sets
    else:
        player_dict['p_score'] = game.p2_score
        player_dict['p_legs'] = game.p2_legs
        player_dict['p_sets'] = game.p2_sets
        player_dict['o_legs'] = game.p1_legs
        player_dict['o_sets'] = game.p1_sets
    return player_dict


def game_from_dict(game, player_dict):
    if game.p1_next_turn:
        game.p1_score = player_dict['p_score']
        game.p1_legs = player_dict['p_legs']
        game.p1_sets = player_dict['p_sets']
        game.p2_legs = player_dict['o_legs']
        game.p2_sets = player_dict['o_sets']
    else:
        game.p2_score = player_dict['p_score']
        game.p2_legs = player_dict['p_legs']
        game.p2_sets = player_dict['p_sets']
        game.p1_legs = player_dict['o_legs']
        game.p1_sets = player_dict['o_sets']
    game.status = player_dict['status']
    return game


def process_leg_win(player_dict, match_json, current_values):
    # check if draws are possible
    set_draw_possible = (player_dict['bo_sets'] % 2) == 0
    leg_draw_possible = (player_dict['bo_legs'] % 2) == 0

    # amount of legs/sets needed to win
    legs_for_set = (player_dict['bo_legs'] / 2) + 1 if leg_draw_possible else math.ceil(player_dict['bo_legs'] / 2)
    sets_for_match = (player_dict['bo_sets'] / 2) + 1 if set_draw_possible else math.ceil(player_dict['bo_sets'] / 2)

    # leg count increase with check for set win
    if player_dict['two_clear_legs']:
        player_dict['p_legs'] += 1
    else:
        player_dict['p_legs'] = (player_dict['p_legs'] + 1) % legs_for_set
    # reset score to default value
    player_dict['p_score'] = player_dict['type']

    # check if player won set
    if player_dict['p_legs'] == 0 or \
            (player_dict['two_clear_legs'] and
             player_dict['p_legs'] >= legs_for_set and
             player_dict['p_legs'] >= player_dict['o_legs'] + 2):
        player_dict['p_sets'] += 1

        # check if player won match or match drawn
        if player_dict['p_sets'] == sets_for_match or \
                (set_draw_possible and (player_dict['p_sets'] == player_dict['o_sets'] == (player_dict['bo_sets'] / 2))):
            # leg score is needed if best of 1 set
            if player_dict['bo_sets'] == 1 and not player_dict['two_clear_legs']:
                player_dict['p_legs'] = math.ceil((player_dict['bo_legs'] + 0.5) / 2)
            player_dict['status'] = 'completed'
            player_dict['p_score'] = 0  # end score 0 looks nicer
        else:  # match not over, new set
            player_dict['p_legs'] = 0
            player_dict['o_legs'] = 0
            current_values['set'] = str(int(current_values['set']) + 1)
            current_values['leg'] = '1'
            match_json[current_values['set']] = {current_values['leg']: {'1': {'scores': [], 'double_missed': []},
                                                                         '2': {'scores': [], 'double_missed': []}}}

    else:  # no new set unless drawn
        # check for drawn set
        if leg_draw_possible and (player_dict['p_legs'] == player_dict['o_legs'] == (player_dict['bo_legs'] / 2)):
            player_dict['p_sets'] += 1
            player_dict['o_sets'] += 1
            # check if a player won the match
            if player_dict['p_sets'] == sets_for_match or player_dict['o_sets'] == sets_for_match:
                player_dict['status'] = 'completed'
                player_dict['p_score'] = 0
            # check if match is drawn - redundant atm, could be merged with game win
            elif set_draw_possible and (player_dict['p_sets'] == player_dict['o_sets'] == (player_dict['bo_sets'] / 2)):
                player_dict['status'] = 'completed'
                player_dict['p_score'] = 0
            # no one won the match, new set
            else:
                player_dict['p_legs'] = 0
                player_dict['o_legs'] = 0
                current_values['set'] = str(int(current_values['set']) + 2)  # + 2 because both players won a set
                current_values['leg'] = '1'
                match_json[current_values['set']] = {current_values['leg']: {'1': {'scores': [], 'double_missed': []},
                                                                             '2': {'scores': [], 'double_missed': []}}}
        else:  # no draw, just new leg
            current_values['leg'] = str(int(current_values['leg']) + 1)
            match_json[current_values['set']][current_values['leg']] = {'1': {'scores': [], 'double_missed': []},
                                                                        '2': {'scores': [], 'double_missed': []}}

    return player_dict, match_json, current_values


def process_score(game, score_value, double_missed, to_finish):
    # game = Game.query.filter_by(hashid=hashid).first_or_404()
    match_json = json.loads(game.match_json)

    if game.status != 'started':
        return game

    current_values = {
        'set': str(game.p1_sets + game.p2_sets + 1),
        'leg': str(game.p1_legs + game.p2_legs + 1),
        'player': '1' if game.p1_next_turn is True else '2'
    }
    player_dict = player_to_dict(game, game.p1_next_turn)
    new_leg_starter = 0  # used for leg starting player

    if to_finish:
        match_json[current_values['set']][current_values['leg']][current_values['player']]['to_finish'] = to_finish
    # bug fix - sometimes to_finish is not sent, default to 3
    elif player_dict['p_score'] - score_value == 0:
        match_json[current_values['set']][current_values['leg']][current_values['player']]['to_finish'] = 3

    match_json[current_values['set']][current_values['leg']][current_values['player']]['double_missed'].append(double_missed)

    # check if leg was won
    if player_dict['p_score'] - score_value == 0:
        # add thrown score to match json object
        match_json[current_values['set']][current_values['leg']][current_values['player']]['scores'].append(score_value)

        # check who begins next leg
        new_leg_starter = '2' \
            if player1_started_leg(match_json[current_values['set']][current_values['leg']]) else '1'
        current_set = current_values['set']

        # check for won sets, won match, update scores etc.
        player_dict, match_json, current_values = process_leg_win(player_dict, match_json, current_values)

        # set mode only: new sets are started alternately, need to recheck leg starter)
        if current_values['set'] > current_set and len(match_json[current_set]) % 2 == 0:
            new_leg_starter = '2' if new_leg_starter == '1' else '1'

        # reset player scores to default
        if not player_dict['status'] == 'completed':
            game.p1_score = game.type
            game.p2_score = game.type
    # check if busted
    elif player_dict['p_score'] - score_value < 0:
        match_json[current_values['set']][current_values['leg']][current_values['player']]['scores'].append(0)
    # Double/Master out: score cannot drop to 1
    elif game.out_mode in ['do', 'mo'] and player_dict['p_score'] - score_value == 1:
        match_json[current_values['set']][current_values['leg']][current_values['player']]['scores'].append(0)
    # nothing special happened, just score
    else:
        player_dict['p_score'] -= score_value
        match_json[current_values['set']][current_values['leg']][current_values['player']]['scores'].append(score_value)

    # save everything back into the model object
    game = game_from_dict(game, player_dict)
    game.match_json = json.dumps(match_json)

    if game.status == 'completed':
        game.end = datetime.utcnow()
        if not game.opponent_type.startswith('computer'):
            broadcast_game_completed(game)
    # new leg
    elif new_leg_starter:
        game.p1_next_turn = True if new_leg_starter == '1' else False
    # no new leg, other player's turn
    else:
        game.p1_next_turn = not game.p1_next_turn
    db.session.commit()
    return game


def current_turn_user_id(hashid):
    game = Game.query.filter_by(hashid=hashid).first_or_404()
    return game.player1 if game.p1_next_turn else game.player2


def process_closest_to_bull(game, score_value, computer=False):
    if score_value > 60:
        return
    closest_to_bull_json = json.loads(game.closest_to_bull_json)
    # local game
    if game.player1 == game.player2:
        player = '2' if (len(closest_to_bull_json['1']) % 3 == 0) and \
                        (len(closest_to_bull_json['1']) > len(closest_to_bull_json['2'])) else '1'
    # computer game
    elif computer:
        player = '2'
    # online game
    else:
        player = '1' if game.player1 == current_user.id else '2'
    other_player = '1' if player == '2' else '2'

    # check if player has to wait for other player
    if len(closest_to_bull_json[player]) % 3 == 0 \
            and len(closest_to_bull_json[player]) > len(closest_to_bull_json[other_player]):
        return

    # append score
    if score_value in (25, 50):
        closest_to_bull_json[player].append(score_value)
    else:
        closest_to_bull_json[player].append(0)
    game.closest_to_bull_json = json.dumps(closest_to_bull_json)
    db.session.commit()

    # check if both threw 3 darts
    if len(closest_to_bull_json[player]) % 3 == 0 \
            and (len(closest_to_bull_json[player]) == len(closest_to_bull_json[other_player])):
        # check if done
        for i in range(len(closest_to_bull_json[player])):
            if closest_to_bull_json['1'][i] > closest_to_bull_json['2'][i]:
                # player 1 won
                game.p1_next_turn = True
                game.closest_to_bull = False
                db.session.commit()
                emit('closest_to_bull_completed', {'hashid': game.hashid, 'p1_won': game.p1_next_turn,
                                                   'p1_score': closest_to_bull_json['1'][-3:],
                                                   'p2_score': closest_to_bull_json['2'][-3:]
                                                   },
                     room=game.hashid, broadcast=True)
                socketio.sleep(0)
                return
            elif closest_to_bull_json['1'][i] < closest_to_bull_json['2'][i]:
                # player 2 won
                game.p1_next_turn = False
                game.closest_to_bull = False
                db.session.commit()
                emit('closest_to_bull_completed', {'hashid': game.hashid, 'p1_won': game.p1_next_turn,
                                                   'p1_score': closest_to_bull_json['1'][-3:],
                                                   'p2_score': closest_to_bull_json['2'][-3:]
                                                   },
                     room=game.hashid, broadcast=True)
                socketio.sleep(0)
                return

        # draw, next round
        emit('closest_to_bull_draw', {'hashid': game.hashid, 'p1_score': closest_to_bull_json['1'][-3:],
                                      'p2_score': closest_to_bull_json['2'][-3:]},
             room=game.hashid, broadcast=True)
        socketio.sleep(0)
        return

    # emit throw score to players
    if len(closest_to_bull_json['1']) % 3 == 1:
        p1_score = closest_to_bull_json['1'][-1:]
    elif len(closest_to_bull_json['1']) % 3 == 2:
        p1_score = closest_to_bull_json['1'][-2:]
    elif len(closest_to_bull_json['1']) % 3 == 0 \
            and len(closest_to_bull_json['1']) > len(closest_to_bull_json['2']):
        p1_score = closest_to_bull_json['1'][-3:]
    else:
        p1_score = []

    if len(closest_to_bull_json['2']) % 3 == 1:
        p2_score = closest_to_bull_json['2'][-1:]
    elif len(closest_to_bull_json['2']) % 3 == 2:
        p2_score = closest_to_bull_json['2'][-2:]
    elif len(closest_to_bull_json['2']) % 3 == 0 \
            and len(closest_to_bull_json['2']) > len(closest_to_bull_json['1']):
        p2_score = closest_to_bull_json['2'][-3:]
    else:
        p2_score = []

    emit('closest_to_bull_score', {'hashid': game.hashid, 'p1_score': p1_score, 'p2_score': p2_score},
         room=game.hashid, broadcast=True)
    socketio.sleep(0)
    return


def broadcast_game_aborted(game):
    emit('game_aborted', {'hashid': game.hashid}, room=game.hashid, namespace='/game', broadcast=True)


def broadcast_online_players(broadcast=True, room='public_chat'):
    status_order = ['lfg', 'online', 'playing', 'busy', 'offline']
    ingame_count = 0
    
    online_players_list = []
    online_thresh_timestamp = datetime.utcnow() - timedelta(minutes=1)
    online_players = User.query

    if room == 'public_chat':
        online_players = online_players.filter(or_(User.is_online, User.last_seen > online_thresh_timestamp))
    else:
        online_players = (
            online_players
            .join(User.tournaments)
            .filter(Tournament.hashid == room)
        )

    online_players = (
        online_players        
        .join(UserStatistic, isouter=True).add_columns(UserStatistic.average, UserStatistic.doubles)
        .join(UserSettings, isouter=True).add_columns(UserSettings.country)
        .join(WebcamSettings, isouter=True).add_columns(WebcamSettings.activated)
        .all()
    )

    online_count = len(online_players)

    for user, average, doubles, country, webcam in online_players:
        socketio.sleep(0)
        status = user.status

        if user.last_seen_ingame and user.last_seen_ingame > (datetime.utcnow() - timedelta(seconds=35)):
            status = 'playing'
            ingame_count += 1

        if user.last_seen and user.last_seen < (datetime.utcnow() - timedelta(seconds=60)):
            status = 'offline'
            online_count -= 1

        avatar = avatars.url(f'{user.id}_thumbnail.jpg') if user.avatar else avatars.url('default.png')
        average = average if average else 0
        doubles = doubles if doubles else 0
        statistics = {'average': average, 'doubles': doubles}

        country = country.lower() if country else None
        webcam = webcam if webcam else False

        online_players_list.append(
            {
                'id': user.id,
                'username': user.username,
                'status': status,
                'status_prio': status_order.index(status),
                'avatar': avatar,
                'statistics': statistics,
                'country': country,
                'is_backer': user.is_backer,
                'webcam': webcam
            }
        )

    online_players_list.sort(key=lambda k: (k['status_prio'], k['username'].lower()))

    if broadcast:
        emit(
            'send_online_players',
            {'players': online_players_list, 'ingame-count': ingame_count, 'online-count': online_count},
            namespace='/chat', room=room,
        )
    else:
        emit(
            'send_online_players', 
            {'players': online_players_list, 'ingame-count': ingame_count, 'online-count': online_count},
            namespace='/chat', room=request.sid
        )


def broadcast_new_game(game):
    room = game.hashid if game.tournament else 'public_chat'
    p1_name, = User.query.with_entities(User.username).filter_by(id=game.player1).first_or_404()
    p2_name, = User.query.with_entities(User.username).filter_by(id=game.player2).first_or_404()

    emit(
        'send_system_message_new_game',
        {'hashid': game.hashid, 'p1_name': p1_name, 'p2_name': p2_name},
        namespace='/chat',
        room=room,
    )
    socketio.sleep(0)

    emit(
        'new_game',
        {
            'hashid': game.hashid,
            'p1_name': p1_name,
            'p2_name': p2_name,
            'tournament': game.tournament,
            'bo_sets': game.bo_sets,
            'bo_legs': game.bo_legs,
        },
        namespace='/game',
        room='new_games',
    )
    socketio.sleep(0)


def broadcast_game_completed(game):
    room = game.tournament if game.tournament else 'public_chat'
    p1_name, = User.query.with_entities(User.username).filter_by(id=game.player1).first_or_404()
    p2_name, = User.query.with_entities(User.username).filter_by(id=game.player2).first_or_404()

    if game.bo_sets > 1:
        p1_score = game.p1_sets
        p2_score = game.p2_sets
    else:
        p1_score = game.p1_legs
        p2_score = game.p2_legs

    emit(
        'send_system_message_game_completed',
        {
            'hashid': game.hashid,
            'p1_name': p1_name,
            'p2_name': p2_name,
            'p1_score': p1_score,
            'p2_score': p2_score,
        },
        namespace='/chat',
        room=room,
    )
    socketio.sleep(0)


def send_notification(username, message, author, type, silent=False):
    emit(
        'send_notification',
        {
            'message': message, 'author': author, 'type': type, 'silent': silent,
        },
        room=username, namespace='/base',
        )
