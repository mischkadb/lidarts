from flask import request
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from lidarts import socketio, db
from lidarts.game.utils import cricket_leg_default
from lidarts.models import CricketGame, User
from lidarts.socket.game.cricket.utils import process_score
from lidarts.socket.utils import current_turn_user_id, process_closest_to_bull
from lidarts.socket.game.cricket.computer import get_computer_score
import json
from datetime import datetime, timedelta
import secrets


def calculate_footer_stats(match_json, last_leg=False):
    stats = {}
    if last_leg:
        if len(match_json[str(len(match_json))]) == 1:
            # last leg is in previous set
            current_set = str(len(match_json) - 1)
            current_leg = str(len(match_json[current_set]))
        else:
            # last leg is in current set
            current_set = str(len(match_json))
            current_leg = str(len(match_json[current_set]) - 1)
    else:
        current_set = str(len(match_json))
        current_leg = str(len(match_json[current_set]))
    p1_current_leg_scores = match_json[current_set][current_leg]['1']['scores']
    p2_current_leg_scores = match_json[current_set][current_leg]['2']['scores']
    stats['p1_current_leg_scores'] = p1_current_leg_scores
    stats['p2_current_leg_scores'] = p2_current_leg_scores
    stats['p1_current_leg_fields'] = match_json[current_set][current_leg]['1']['fields']
    stats['p2_current_leg_fields'] = match_json[current_set][current_leg]['2']['fields']
    # various statistics for footer
    p1_marks = 0
    for scores in p1_current_leg_scores:
        for score in scores:
            if score == 0:
                continue
            elif 0 < score <= 25:
                p1_marks += 1
            elif 25 < score <= 40 or score == 50:
                p1_marks += 2
            else:
                p1_marks += 3

    p2_marks = 0
    for scores in p2_current_leg_scores:
        for score in scores:
            if score == 0:
                continue
            elif 0 < score <= 25:
                p2_marks += 1
            elif 25 < score <= 40 or score == 50:
                p2_marks += 2
            else:
                p2_marks += 3
       

    stats['p1_leg_mpr'] = round(p1_marks / len(p1_current_leg_scores), 2) if len(p1_current_leg_scores) else 0
    stats['p2_leg_mpr'] = round(p2_marks / len(p2_current_leg_scores), 2) if len(p2_current_leg_scores) else 0

    p1_marks = 0
    p2_marks = 0
    p1_rounds = 0
    p2_rounds = 0

    for set in match_json:
        for leg in match_json[set]:
            p1_rounds += len(match_json[set][leg]['1']['scores'])
            p2_rounds += len(match_json[set][leg]['2']['scores'])
            for scores in match_json[set][leg]['1']['scores']:
                for score in scores:
                    if score == 0:
                        continue
                    elif 0 < score <= 25:
                        p1_marks += 1
                    elif 25 < score <= 40 or score == 50:
                        p1_marks += 2
                    else:
                        p1_marks += 3

            for scores in match_json[set][leg]['2']['scores']:
                for score in scores:
                    if score == 0:
                        continue
                    elif 0 < score <= 25:
                        p2_marks += 1
                    elif 25 < score <= 40 or score == 50:
                        p2_marks += 2
                    else:
                        p2_marks += 3

    stats['p1_match_mpr'] = round(p1_marks / p1_rounds, 2) if p1_rounds else 0
    stats['p2_match_mpr'] = round(p2_marks / p2_rounds, 2) if p2_rounds else 0

    return stats


def send_score_response(game, p1_old_score=0, p2_old_score=0, broadcast=False):
    match_json = json.loads(game.match_json)
    stats = calculate_footer_stats(match_json)

    computer_game = game.opponent_type.startswith('computer')

    if not stats['p1_current_leg_scores'] and not stats['p2_current_leg_scores']:
        broadcast = False

    emit('score_response',
         {'hashid': game.hashid,
          'p1_score': game.p1_score, 'p2_score': game.p2_score, 'p1_sets': game.p1_sets,
          'p2_sets': game.p2_sets, 'p1_legs': game.p1_legs, 'p2_legs': game.p2_legs,
          'p1_next_turn': game.p1_next_turn, 'p1_current_leg': stats['p1_current_leg_scores'],
          'p2_current_leg': stats['p2_current_leg_scores'],
          'p1_old_score': p1_old_score, 'p2_old_score': p2_old_score,
          'p1_current_fields': stats['p1_current_leg_fields'], 'p2_current_fields': stats['p2_current_leg_fields'],
          'p1_leg_mpr': stats['p1_leg_mpr'], 'p2_leg_mpr': stats['p2_leg_mpr'],
          'p1_match_mpr': stats['p1_match_mpr'], 'p2_match_mpr': stats['p2_match_mpr'],
          'computer_game': computer_game,
          'p1_id': game.player1, 'p2_id': game.player2,
          'new_score': broadcast  # needed for score sound output
          },

         room=game.hashid, broadcast=broadcast)


@socketio.on('connect', namespace='/game/cricket')
def connect():
    print('Client connected', request.sid)


@socketio.on('player_heartbeat', namespace='/game/cricket')
def player_heartbeat(message):
    if current_user.is_authenticated:
        game = CricketGame.query.filter_by(hashid=message['hashid']).first_or_404()
        current_user.last_seen_ingame = datetime.utcnow()
        p1 = User.query.filter_by(id=game.player1).first_or_404()
        p1_ingame = p1.last_seen_ingame > datetime.utcnow() - timedelta(seconds=10)
        p2 = User.query.filter_by(id=game.player2).first_or_404() if game.player2 else None
        p2_ingame = p2.last_seen_ingame > datetime.utcnow() - timedelta(seconds=10) if p2 else True
        db.session.commit()
        emit('players_ingame', {'p1_ingame': p1_ingame, 'p2_ingame': p2_ingame}, room=game.hashid, broadcast=True)


@socketio.on('init', namespace='/game/cricket')
def init(message):
    game = CricketGame.query.filter_by(hashid=message['hashid']).first_or_404()
    if not game:
        return
    join_room(game.hashid)
    if game.closest_to_bull:
        return
    send_score_response(game, broadcast=False)


@socketio.on('init_waiting', namespace='/game/cricket')
def init_waiting(message):
    game = CricketGame.query.filter_by(hashid=message['hashid']).first_or_404()
    join_room(game.hashid)


@socketio.on('send_rematch_offer', namespace='/game/cricket')
def send_rematch_offer(message):
    emit('rematch_offer', room=message['hashid'], namespace='/game/cricket')


@socketio.on('accept_rematch_offer', namespace='/game/cricket')
def accept_rematch_offer(message):
    hashid = create_rematch(message['hashid'])
    emit('start_rematch', {'hashid': hashid}, room=message['hashid'], namespace='/game/cricket')


def create_rematch(hashid):
    game = CricketGame.query.filter_by(hashid=hashid).first_or_404()

    match_json = json.dumps(
        {
            1: {
                1: cricket_leg_default.copy()
            }
        }
    )

    rematch = CricketGame(
        player1=game.player1, player2=game.player2,
        bo_sets=game.bo_sets, bo_legs=game.bo_legs,
        two_clear_legs=game.two_clear_legs,
        p1_sets=0, p2_sets=0, p1_legs=0, p2_legs=0,
        p1_score=0, p2_score=0,
        begin=datetime.utcnow(), match_json=match_json,
        status='started', opponent_type=game.opponent_type,
        public_challenge=False,
        tournament=game.tournament, 
        score_input_delay=game.score_input_delay,
        webcam=game.webcam, jitsi_hashid=secrets.token_urlsafe(8)[:8],
        variant='cricket',
    )
    rematch.p1_next_turn = True
    if game.closest_to_bull_json:
        closest_to_bull_json = json.dumps({1: [], 2: []})
        rematch.closest_to_bull_json = closest_to_bull_json
        rematch.closest_to_bull = True
    db.session.add(rematch)
    db.session.commit()  # needed to get a game id for the hashid
    rematch.set_hashid()
    db.session.commit()

    return rematch.hashid


@socketio.on('send_score', namespace='/game/cricket')
def send_score(message):
    hashid = message['hashid']
    game = CricketGame.query.filter_by(hashid=hashid).first()

    if 'computer' in message and not game.p1_next_turn:
        # calculate computer's score
        message['score'] = get_computer_score(message['hashid'])
    # players may throw simultaneously at closest to bull
    # exception needed for undoing score if it's not your turn
    elif int(message['user_id']) != current_turn_user_id(message['hashid'], True) and not game.closest_to_bull \
            and not message['undo_active']:
        return
    # spectators should never submit scores :-)
    elif int(message['user_id']) not in (game.player1, game.player2):
        return

    score_value = int(message['score'])
    if score_value not in (15, 16, 17, 18, 19, 20, 25, 30, 32, 34, 36, 38, 40, 45, 48, 50, 51, 54, 57, 60):
        score_value = 0

    # Closest to bull handler to determine starting player
    if game.closest_to_bull:
        process_closest_to_bull(game, score_value)
        if game.opponent_type.startswith('computer'):
            # computer's attempt at double bullseye
            score = get_computer_score(game.hashid)
            process_closest_to_bull(game, score, computer=True)
        return

    match_json = json.loads(game.match_json)

    # undo input handler
    # TODO: undo handling
    if 'undo_active' in message and message['undo_active'] is True:
        current_set = str(game.p1_sets + game.p2_sets + 1)
        current_leg = str(game.p1_legs + game.p2_legs + 1)

        if current_user.id == game.player1 and current_user.id == game.player2:
            undo_player = '2' if game.p1_next_turn else '1'
        elif current_user.id == game.player1:
            undo_player = '1'
        else:
            undo_player = '2'

        # if no checkout just change score silently
        if sum(match_json[current_set][current_leg][undo_player]['scores'][:-1]) + score_value > game.type:
            match_json[current_set][current_leg][undo_player]['scores'][-1] = 0
            match_json[current_set][current_leg][undo_player]['double_missed'][-1] = int(message['double_missed'])
            if undo_player == '1':
                game.p1_score = game.type - sum(match_json[current_set][current_leg][undo_player]['scores'])
            else:
                game.p2_score = game.type - sum(match_json[current_set][current_leg][undo_player]['scores'])
            game.match_json = json.dumps(match_json)
            db.session.commit()
            send_score_response(game, broadcast=False)
            return
        elif sum(match_json[current_set][current_leg][undo_player]['scores'][:-1]) + score_value < game.type:
            match_json[current_set][current_leg][undo_player]['scores'][-1] = score_value
            match_json[current_set][current_leg][undo_player]['double_missed'][-1] = int(message['double_missed'])
            if undo_player == '1':
                game.p1_score = game.type - sum(match_json[current_set][current_leg][undo_player]['scores'])
            else:
                game.p2_score = game.type - sum(match_json[current_set][current_leg][undo_player]['scores'])
            game.match_json = json.dumps(match_json)
            db.session.commit()
            send_score_response(game, broadcast=False)
            return
        # checkout - revert scores and proceed normally
        else:
            # rollback to handle end of leg
            if (undo_player == '1' and game.p1_next_turn) or (undo_player == '2' and not game.p1_next_turn):
                # other player already entered score - rollback both, don't change p1_next_turn
                match_json[current_set][current_leg]['1']['scores'].pop()
                match_json[current_set][current_leg]['1']['double_missed'].pop()
                match_json[current_set][current_leg]['2']['scores'].pop()
                match_json[current_set][current_leg]['2']['double_missed'].pop()
                game.p1_score = game.type - sum(match_json[current_set][current_leg]['1']['scores'])
                game.p2_score = game.type - sum(match_json[current_set][current_leg]['2']['scores'])
            else:
                # other player did not enter score - rollback undo player, toggle p1_next_turn
                match_json[current_set][current_leg][undo_player]['scores'].pop()
                match_json[current_set][current_leg][undo_player]['double_missed'].pop()
                game.p1_next_turn = not game.p1_next_turn
                if undo_player == '1':
                    game.p1_score = game.type - sum(match_json[current_set][current_leg][undo_player]['scores'])
                else:
                    game.p2_score = game.type - sum(match_json[current_set][current_leg][undo_player]['scores'])
            game.match_json = json.dumps(match_json)
            db.session.commit()

    # keep old score to display game shot if finish
    p1_old_score = game.p1_score
    p2_old_score = game.p2_score
    old_set_count = len(match_json)
    old_leg_count = len(match_json[str(len(match_json))])

    socketio.sleep(0)
    game = process_score(game, score_value)
    socketio.sleep(0)
    # check for match_json updates
    match_json = json.loads(game.match_json)

    if game.status == 'completed':
        last_set = match_json[str(len(match_json))]
        last_leg = last_set[str(len(last_set))]
        p1_last_score = last_leg['1']['points']
        p2_last_score = last_leg['2']['points']
        p1_won = last_leg['1']['points'] > last_leg['2']['points']
        stats = calculate_footer_stats(match_json)
        emit(
            'game_completed',
            {
                'hashid': game.hashid, 'p1_won': p1_won,
                'p1_last_score': p1_last_score, 'p2_last_score': p2_last_score,
                'p1_old_score': p1_old_score, 'p2_old_score': p2_old_score,
                'p1_sets': game.p1_sets, 'p2_sets': game.p2_sets,
                'p1_legs': game.p1_legs, 'p2_legs': game.p2_legs,
                'p1_next_turn': game.p1_next_turn, 'p1_current_leg': stats['p1_current_leg_scores'],
                'p2_current_leg': stats['p2_current_leg_scores'],
                'p1_current_fields': stats['p1_current_leg_fields'], 'p2_current_fields': stats['p2_current_leg_fields'],
                'p1_leg_mpr': stats['p1_leg_mpr'], 'p2_leg_mpr': stats['p2_leg_mpr'],
                'p1_match_mpr': stats['p1_match_mpr'], 'p2_match_mpr': stats['p2_match_mpr'],
            },
            room=game.hashid,
            broadcast=True,
            namespace='/game/cricket'
        )

    elif old_set_count < len(match_json) or old_leg_count < len(match_json[str(len(match_json))]):
        if len(match_json[str(len(match_json))]) == 1:  # new set
            last_set = match_json[str(len(match_json)-1)]
            last_leg = last_set[str(len(last_set))]
        else:  # no new set
            last_set = match_json[str(len(match_json))]
            last_leg = last_set[str(len(last_set)-1)]
        p1_last_score = last_leg['1']['points']
        p2_last_score = last_leg['2']['points']
        p1_won = last_leg['1']['points'] > last_leg['2']['points']
        stats = calculate_footer_stats(match_json, last_leg=True)
        emit('game_shot', {'hashid': game.hashid, 'p1_last_score': p1_last_score, 'p2_last_score': p2_last_score,
                           'p1_old_score': p1_old_score, 'p2_old_score': p2_old_score,
                           'p1_won': p1_won, 'p1_sets': game.p1_sets,
                           'p2_sets': game.p2_sets, 'p1_legs': game.p1_legs, 'p2_legs': game.p2_legs,                           
                            'p1_next_turn': game.p1_next_turn, 'p1_current_leg': stats['p1_current_leg_scores'],
                            'p2_current_leg': stats['p2_current_leg_scores'],
                            'p1_current_fields': stats['p1_current_leg_fields'], 'p2_current_fields': stats['p2_current_leg_fields'],
                            'p1_leg_mpr': stats['p1_leg_mpr'], 'p2_leg_mpr': stats['p2_leg_mpr'],
                            'p1_match_mpr': stats['p1_match_mpr'], 'p2_match_mpr': stats['p2_match_mpr'],
                           },
             room=game.hashid, broadcast=True, namespace='/game/cricket')
    else:
        send_score_response(game, p1_old_score, p2_old_score, broadcast=True)


@socketio.on('get_score_after_leg_win', namespace='/game/cricket')
def get_score_after_leg_win(message):
    if not message['hashid']:
        return
    hashid = message['hashid']
    game = CricketGame.query.filter_by(hashid=hashid).first()
    send_score_response(game, broadcast=True)
    if game.status == 'completed':
        emit('game_completed', room=game.hashid, broadcast=True)
        leave_room(game.hashid)


@socketio.on('undo_request_remaining_score', namespace='/game/cricket')
def undo_get_remaining_score(message):
    if not message['hashid']:
        return
    hashid = message['hashid']
    game = Game.query.filter_by(hashid=hashid).first()
    if current_user.is_authenticated:
        match_json = json.loads(game.match_json)
        current_set = str(game.p1_sets + game.p2_sets + 1)
        current_leg = str(game.p1_legs + game.p2_legs + 1)
        current_leg_json = match_json[current_set][current_leg]
        if current_user.id == game.player1 and current_user.id == game.player2:
            # local game, last entered score is undone
            # check if there is score in current leg to undo
            if (game.p1_next_turn and len(current_leg_json['2']['scores']) == 0) \
                    or (not game.p1_next_turn and len(current_leg_json['1']['scores']) == 0):
                return 'no score to undo'
            # calculate remaining score without last entered score
            remaining_score = game.type - sum(current_leg_json['2']['scores'][:-1]) \
                if game.p1_next_turn else game.type - sum(current_leg_json['1']['scores'][:-1])
        elif current_user.id == game.player1:
            # check if there is score in current leg to undo
            if len(current_leg_json['1']['scores']) == 0:
                return 'no score to undo'
            # get last remaining score from player 1
            remaining_score = game.type - sum(current_leg_json['1']['scores'][:-1])
        else:
            # check if there is score in current leg to undo
            if len(current_leg_json['2']['scores']) == 0:
                return 'no score to undo'
            # get last remaining score from player 2
            remaining_score = game.type - sum(current_leg_json['2']['scores'][:-1])
        emit('undo_remaining_score',
             {'remaining_score': remaining_score, 'score_value': message['score_value']})


@socketio.on('disconnect', namespace='/game/cricket')
def disconnect():
    print('Client disconnected', request.sid)
