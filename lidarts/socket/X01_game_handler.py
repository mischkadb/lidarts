from flask import current_app, request
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from lidarts import socketio, db
from lidarts.game.checkout_suggestions import checkout_suggestions
from lidarts.models import Game
from lidarts.socket.utils import process_score, current_turn_user_id, process_closest_to_bull
from lidarts.socket.computer import get_computer_score
import json
from datetime import datetime
import secrets


def send_score_response(game, old_score=0, broadcast=False):
    match_json = json.loads(game.match_json)
    current_set = str(len(match_json))
    current_leg = str(len(match_json[str(len(match_json))]))
    p1_current_leg_scores = match_json[current_set][current_leg]['1']['scores']
    p2_current_leg_scores = match_json[current_set][current_leg]['2']['scores']
    # various statistics for footer
    p1_leg_avg = round(sum(p1_current_leg_scores) / len(p1_current_leg_scores), 2) if len(p1_current_leg_scores) else 0
    p2_leg_avg = round(sum(p2_current_leg_scores) / len(p2_current_leg_scores), 2) if len(p2_current_leg_scores) else 0

    p1_180 = 0
    p2_180 = 0
    p1_140 = 0
    p2_140 = 0
    p1_100 = 0
    p2_100 = 0
    p1_scores = []
    p2_scores = []
    p1_first9_scores = []
    p2_first9_scores = []
    p1_high_finish = 0
    p2_high_finish = 0
    p1_short_leg = 0
    p2_short_leg = 0

    p1_darts_thrown = 0
    p1_darts_thrown_double = 0
    p1_legs_won = 0
    p2_darts_thrown = 0
    p2_darts_thrown_double = 0
    p2_legs_won = 0

    for set in match_json:
        for leg in match_json[set]:
            socketio.sleep(0)
            p1_darts_thrown_double += sum(match_json[set][leg]['1']['double_missed'])
            p2_darts_thrown_double += sum(match_json[set][leg]['2']['double_missed'])

            p1_darts_thrown_this_leg = len(match_json[set][leg]['1']['scores']) * 3
            p2_darts_thrown_this_leg = len(match_json[set][leg]['2']['scores']) * 3

            if sum(match_json[set][leg]['1']['scores']) == game.type:
                if 'to_finish' in match_json[set][leg]['1']:
                    p1_darts_thrown_this_leg -= (3 - match_json[set][leg]['1']['to_finish'])

                p1_darts_thrown_double += 1
                p1_legs_won += 1

                p1_short_leg = p1_darts_thrown_this_leg if p1_short_leg == 0 else p1_short_leg
                p1_short_leg = p1_darts_thrown_this_leg \
                    if p1_darts_thrown_this_leg < p1_short_leg else p1_short_leg
                p1_high_finish = match_json[set][leg]['1']['scores'][-1] \
                    if match_json[set][leg]['1']['scores'][-1] > p1_high_finish else p1_high_finish

            if sum(match_json[set][leg]['2']['scores']) == game.type:
                if 'to_finish' in match_json[set][leg]['2']:
                    p2_darts_thrown_this_leg -= (3 - match_json[set][leg]['2']['to_finish'])

                p2_darts_thrown_double += 1  # better: p2_darts_thrown_double = legs_won + double_missed
                p2_legs_won += 1

                p2_short_leg = p2_darts_thrown_this_leg if p2_short_leg == 0 else p2_short_leg
                p2_short_leg = p2_darts_thrown_this_leg \
                    if p2_darts_thrown_this_leg < p2_short_leg else p2_short_leg
                p2_high_finish = match_json[set][leg]['2']['scores'][-1] \
                    if match_json[set][leg]['2']['scores'][-1] > p2_high_finish else p2_high_finish

            p1_darts_thrown += p1_darts_thrown_this_leg
            p2_darts_thrown += p2_darts_thrown_this_leg

            for i, score in enumerate(match_json[set][leg]['1']['scores']):
                p1_scores.append(score)
                if i <= 2:
                    p1_first9_scores.append(score)
                if score == 180:
                    p1_180 += 1
                elif score >= 140:
                    p1_140 += 1
                elif score >= 100:
                    p1_100 += 1

            for i, score in enumerate(match_json[set][leg]['2']['scores']):
                p2_scores.append(score)
                if i <= 2:
                    p2_first9_scores.append(score)
                if score == 180:
                    p2_180 += 1
                elif score >= 140:
                    p2_140 += 1
                elif score >= 100:
                    p2_100 += 1

    p1_match_avg = round(sum(p1_scores) * 3 / (p1_darts_thrown), 2) if p1_scores else 0
    p2_match_avg = round(sum(p2_scores) * 3 / (p2_darts_thrown), 2) if p2_scores else 0
    p1_first9_avg = round(sum(p1_first9_scores)/len(p1_first9_scores), 2) if p1_first9_scores else 0
    p2_first9_avg = round(sum(p2_first9_scores)/len(p2_first9_scores), 2) if p2_first9_scores else 0

    p1_doubles = int(p1_legs_won / p1_darts_thrown_double * 10000) / 100 if p1_legs_won and p1_darts_thrown_double else 0
    p2_doubles = int(p2_legs_won / p2_darts_thrown_double * 10000) / 100 if p2_legs_won and p2_darts_thrown_double else 0

    p1_started_leg = (
        len(p1_current_leg_scores) > len(p2_current_leg_scores) 
        or (len(p1_current_leg_scores) == len(p2_current_leg_scores) and game.p1_next_turn)
    )
    p2_started_leg = not p1_started_leg

    p1_checkout_suggestion = checkout_suggestions[game.p1_score].replace('-', ' ') if game.p1_score in checkout_suggestions else None
    p2_checkout_suggestion = checkout_suggestions[game.p2_score].replace('-', ' ') if game.p2_score in checkout_suggestions else None

    computer_game = game.opponent_type.startswith('computer')

    room = game.hashid if broadcast else request.sid

    emit(
        'score_response',
        {
            'hashid': game.hashid,
            'p1_score': game.p1_score, 'p2_score': game.p2_score, 'p1_sets': game.p1_sets,
            'p2_sets': game.p2_sets, 'p1_legs': game.p1_legs, 'p2_legs': game.p2_legs,
            'p1_next_turn': game.p1_next_turn, 'p1_current_leg': p1_current_leg_scores,
            'p2_current_leg': p2_current_leg_scores, 'old_score': old_score,
            'p1_leg_avg': p1_leg_avg, 'p2_leg_avg': p2_leg_avg,
            'p1_match_avg': p1_match_avg, 'p2_match_avg': p2_match_avg,
            'p1_first9_avg': p1_first9_avg, 'p2_first9_avg': p2_first9_avg,
            'p1_100': p1_100, 'p2_100': p2_100,
            'p1_140': p1_140, 'p2_140': p2_140,
            'p1_180': p1_180, 'p2_180': p2_180,
            'p1_doubles': p1_doubles, 'p2_doubles': p2_doubles,
            'p1_legs_won': p1_legs_won, 'p2_legs_won': p2_legs_won,
            'p1_darts_thrown_double': p1_darts_thrown_double, 'p2_darts_thrown_double': p2_darts_thrown_double,
            'p1_high_finish': p1_high_finish, 'p2_high_finish': p2_high_finish,
            'p1_short_leg': p1_short_leg, 'p2_short_leg': p2_short_leg,
            'computer_game': computer_game,
            'p1_id': game.player1, 'p2_id': game.player2,
            'p1_started_leg': p1_started_leg, 'p2_started_leg': p2_started_leg,
            'p1_checkout_suggestion': p1_checkout_suggestion, 'p2_checkout_suggestion': p2_checkout_suggestion, 
            'new_score': broadcast  # needed for score sound output
        },
        room=room)
    socketio.sleep(0)


def create_rematch(hashid):
    game = Game.query.filter_by(hashid=hashid).first_or_404()

    match_json = json.dumps(
        {
            1: {
                1: {
                    1: {
                        'scores': [],
                        'double_missed': []
                        },
                    2: {
                        'scores': [],
                        'double_missed': []
                        }
                    }
                }
        }
    )

    rematch = Game(
        player1=game.player1, player2=game.player2, type=game.type,
        bo_sets=game.bo_sets, bo_legs=game.bo_legs,
        two_clear_legs=game.two_clear_legs,
        p1_sets=0, p2_sets=0, p1_legs=0, p2_legs=0,
        p1_score=int(game.type), p2_score=int(game.type),
        in_mode=game.in_mode, out_mode=game.out_mode,
        begin=datetime.utcnow(), match_json=match_json,
        status='started', opponent_type=game.opponent_type,
        public_challenge=False,
        tournament=game.tournament, 
        score_input_delay=game.score_input_delay,
        webcam=game.webcam, jitsi_hashid=secrets.token_urlsafe(8)[:8],
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


@socketio.on('connect', namespace='/game')
def connect():
    # print('Client connected', request.sid)
    pass


@socketio.on('player_heartbeat', namespace='/game')
def player_heartbeat(message):
    user_id = message['user_id']
    current_app.redis.sadd('last_seen_ingame_bulk_user_ids', user_id)
    #current_user.last_seen_ingame = datetime.utcnow()
    #db.session.commit()
    emit('player_heartbeat_response', {'player_id_heartbeat': user_id}, room=f'{message["hashid"]}_heartbeats')


@socketio.on('init', namespace='/game')
def init(message):
    game = Game.query.filter_by(hashid=message['hashid']).first_or_404()
    join_room(game.hashid)

    if 'heartbeats' in message:
        join_room(f'{game.hashid}_heartbeats')
    if game.closest_to_bull:
        return

    send_score_response(game, broadcast=False)


@socketio.on('listen_new_games', namespace='/game')
def init(message):
    join_room('new_games')


@socketio.on('init_waiting', namespace='/game')
def init_waiting(message):
    game = Game.query.filter_by(hashid=message['hashid']).first_or_404()
    join_room(game.hashid)


@socketio.on('start_game', namespace='/game')
def start_game(hashid):
    emit('start_game', room=hashid, broadcast=True, namespace='/game')


@socketio.on('send_rematch_offer', namespace='/game')
def send_rematch_offer(message):
    emit('rematch_offer', room=message['hashid'], namespace='/game')


@socketio.on('accept_rematch_offer', namespace='/game')
def accept_rematch_offer(message):
    hashid = create_rematch(message['hashid'])
    emit('start_rematch', {'hashid': hashid}, room=message['hashid'], namespace='/game')


@socketio.on('send_score', namespace='/game')
def send_score(message):
    hashid = message['hashid']
    game = Game.query.filter_by(hashid=hashid).first()

    if 'computer' in message and not game.p1_next_turn:
        # calculate computer's score
        message['score'], message['double_missed'], message['to_finish'] = get_computer_score(message['hashid'])
        socketio.sleep(0)
    elif 'score' not in message or not message['score']:
        return
    # players may throw simultaneously at closest to bull
    # exception needed for undoing score if it's not your turn
    elif int(message['user_id']) != current_turn_user_id(message['hashid']) and not game.closest_to_bull \
            and not message['undo_active']:
        return
    # spectators should never submit scores :-)
    elif int(message['user_id']) not in (game.player1, game.player2):
        return

    try:
        score_value = int(message['score'])
        impossible_numbers = [179, 178, 176, 175, 173, 172, 169]
        if not 0 <= score_value <= 180 or score_value in impossible_numbers:
            return
    except:
        return

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
    old_score = game.p1_score if game.p1_next_turn else game.p2_score
    old_set_count = len(match_json)
    old_leg_count = len(match_json[str(len(match_json))])

    socketio.sleep(0)
    game = process_score(game, score_value, int(message['double_missed']), int(message['to_finish']))
    socketio.sleep(0)
    
    # check for match_json updates
    match_json = json.loads(game.match_json)

    if game.status == 'completed':
        last_set = match_json[str(len(match_json))]
        last_leg = last_set[str(len(last_set))]
        p1_last_leg = last_leg['1']['scores']
        p2_last_leg = last_leg['2']['scores']
        p1_won = sum(p1_last_leg) == game.type

        # calculate cached stats
        if game.type == 501 and game.in_mode == 'si' and game.out_mode == 'do':
            rq_job = current_app.task_queue.enqueue('lidarts.tasks.calc_cached_stats', game.player1)
            if game.player2 and game.player1 != game.player2:
                rq_job = current_app.task_queue.enqueue('lidarts.tasks.calc_cached_stats', game.player2)

        emit(
            'game_completed',
            {
                'hashid': game.hashid,
                'p1_last_leg': p1_last_leg,
                'p2_last_leg': p2_last_leg,
                'p1_won': p1_won,
                'type': game.type,
                'p1_sets': game.p1_sets,
                'p2_sets': game.p2_sets,
                'p1_legs': game.p1_legs,
                'p2_legs': game.p2_legs,
                'to_finish': message['to_finish'],
            },
            room=game.hashid,
            broadcast=True,
            namespace='/game'
        )

    elif old_set_count < len(match_json) or old_leg_count < len(match_json[str(len(match_json))]):
        if len(match_json[str(len(match_json))]) == 1:  # new set
            last_set = match_json[str(len(match_json)-1)]
            last_leg = last_set[str(len(last_set))]
        else:  # no new set
            last_set = match_json[str(len(match_json))]
            last_leg = last_set[str(len(last_set)-1)]
        p1_last_leg = last_leg['1']['scores']
        p2_last_leg = last_leg['2']['scores']
        p1_won = sum(p1_last_leg) == game.type
        emit(
            'game_shot',
            {
                'hashid': game.hashid,
                'p1_last_leg': p1_last_leg,
                'p2_last_leg': p2_last_leg,
                'p1_won': p1_won,
                'type': game.type,
                'p1_sets': game.p1_sets,
                'p2_sets': game.p2_sets,
                'p1_legs': game.p1_legs,
                'p2_legs': game.p2_legs,
                'to_finish': message['to_finish'],
            },
            room=game.hashid,
            broadcast=True,
            namespace='/game'
        )
    else:
        send_score_response(game, old_score, broadcast=True)


@socketio.on('get_score_after_leg_win', namespace='/game')
def get_score_after_leg_win(message):
    if not message['hashid']:
        return
    hashid = message['hashid']
    game = Game.query.filter_by(hashid=hashid).first()
    send_score_response(game, broadcast=True)
    if game.status == 'completed':
        emit('game_completed', room=game.hashid, broadcast=True)
        leave_room(game.hashid)


@socketio.on('undo_request_remaining_score', namespace='/game')
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


@socketio.on('disconnect', namespace='/game')
def disconnect():
    # print('Client disconnected', request.sid)
    pass

