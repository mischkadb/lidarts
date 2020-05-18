import math
from collections import deque
from lidarts import db
from lidarts.tournament.models import BracketGame
from lidarts.models import TournamentGame, Game
import json
from datetime import datetime


def generate_upper_bracket(num_players):
    num_rounds_upper = math.ceil(math.log2(num_players))
    matches = []
    prev_order = []
    match_id = 1

    for round_ in range(num_rounds_upper):
        this_order = prev_order
        prev_order = []
        matches_in_round = int(math.pow(2, round_))
        round_matches = []
        for match in range(1, matches_in_round + 1):
            game = BracketGame(match_id)
            game.p1 = match
            game.p2 = matches_in_round*2+1-match
            round_matches.append(game)
        if this_order:
            round_matches.sort(key=lambda x: this_order.index(x.p1))
        for game in round_matches:
            prev_order.append(game.p1)
            prev_order.append(game.p2)
        matches.append(round_matches)

    games_upper = []
    for i, round_ in enumerate(matches):
        round_matches = []
        for game in round_:
            game.id_ = match_id
            if i < num_rounds_upper - 1:
                game.p1 = None
                game.p2 = None
                game.p1_winner_from = game.id_*2
                game.p2_winner_from = game.id_*2+1
            round_matches.append(game)
            match_id += 1
        games_upper.append(round_matches)
    games_upper.reverse()

    return games_upper


def generate_lower_bracket(num_players):
    loser_rotation = deque(['inverse', 'inverse half', 'regular half', 'regular', 'inverse', 'regular'])

    match_id = num_players
    matches = []
    num_rounds_upper = math.ceil(math.log2(num_players))
    num_rounds_lower = math.ceil(math.log2(num_players / 2)) * 2
    matches_in_last_round = 0
    for round_ in range(num_rounds_lower):
        matches_in_round = int(math.pow(2, math.floor(round_ / 2)))
        new_losers = matches_in_round > matches_in_last_round
        round_matches = (new_losers, [])
        for match in range(1, matches_in_round + 1):
            game = BracketGame(match_id)
            if not new_losers and round_ >= num_rounds_lower - 1:               
                game.p1_loser_from = int(math.pow(2, num_rounds_upper - 1)) + (match * 2) - 2
                game.p2_loser_from = int(math.pow(2, num_rounds_upper - 1)) + (match * 2) - 1
            round_matches[1].append(game)
            match_id += 1
        matches.append(round_matches)
        matches_in_last_round = matches_in_round

    matches.reverse()
    games_lower = [] 
    prev_round = []
    for (new_losers, round_) in matches:
        if new_losers:
            losers = [len(round_) + x for x in range(len(round_))]
            if loser_rotation[0] == 'inverse':
                losers.reverse()
            elif loser_rotation[0] == 'regular half':
                losers = losers[len(losers) // 2:] + losers[:len(losers) // 2]
            elif loser_rotation[0] == 'inverse half':
                losers.reverse()
                losers = losers[len(losers) // 2:] + losers[:len(losers) // 2]
            loser_rotation.rotate(-1)
        round_matches = []
        for i, game in enumerate(round_):
            if prev_round:
                if new_losers:
                    game.p1_loser_from = losers[i]
                    game.p2_winner_from = prev_round[i].id_
                else:
                    game.p1_winner_from = prev_round[i*2].id_
                    game.p2_winner_from = prev_round[i*2+1].id_
            round_matches.append(game)

        prev_round = round_matches
        games_lower.append(round_matches)

    return games_lower


def add_bracket_ids(games_upper, games_lower):
    w = 0
    l = 0
    winners_next = True
    bracket_id = 1
    games_upper_bracket_ids = []
    games_lower_bracket_ids = []
    while w < len(games_upper) or l < len(games_lower):
        if winners_next:
            round_games = []
            for game in games_upper[w]:
                if game.winner:
                    continue
                game.bracket_id = bracket_id
                bracket_id += 1
                round_games.append(game)
            w += 1
            winners_next = False
            games_upper_bracket_ids.append(round_games)
        else:
            round_games = []
            for game in games_lower[l]:
                if game.winner:
                    continue
                game.bracket_id = bracket_id
                bracket_id += 1
                round_games.append(game)
            if l == 0 or len(games_lower[l]) != len(games_lower[l-1]):
                winners_next = True
            l += 1
            games_lower_bracket_ids.append(round_games)

    return games_upper_bracket_ids, games_lower_bracket_ids


def add_bracket_ids_single_elim(games_upper):
    bracket_id = 1
    games_upper_bracket_ids = []
    for rounds_ in games_upper:
        round_games = []
        for game in rounds_:
            if game.winner:
                continue
            game.bracket_id = bracket_id
            bracket_id += 1
            round_games.append(game)
        games_upper_bracket_ids.append(round_games)

    return games_upper_bracket_ids


def add_players(num_players, games_upper, games_lower=None):
    for i, game in enumerate(games_upper[0]):
        game.p2 = game.p2 if game.p2 <= num_players else None
        if not game.p2:
            game.winner = game.p1
            if not games_upper[1][math.floor(i / 2)].p1:
                games_upper[1][math.floor(i / 2)].p1 = game.p1
                games_upper[1][math.floor(i / 2)].p1_winner_from = None
            else:
                games_upper[1][math.floor(i / 2)].p2 = game.p1
                games_upper[1][math.floor(i / 2)].p2_winner_from = None

    if not games_lower:
        return

    for i, game in enumerate(games_lower[0]):
        if games_upper[0][i*2].winner:
            game.p1_loser_from = None
        if games_upper[0][i*2 + 1].winner:
            game.p2_loser_from = None
        if not game.p1_loser_from and not game.p2_loser_from:
            game.winner = True
            games_lower[1][i].p2_winner_from = None
        elif not game.p1_loser_from:
            game.winner = True
            games_lower[1][i].p2_loser_from = game.p2_loser_from
            games_lower[1][i].p2_winner_from = None

    for i, game in enumerate(games_lower[1]):
        if not game.p2_winner_from and not game.p2_loser_from:
            game.winner = True
            if i % 2 == 0:
                games_lower[2][math.floor(i / 2)].p1_winner_from = None
                games_lower[2][math.floor(i / 2)].p1_loser_from = game.p1_loser_from
            else:
                games_lower[2][math.floor(i / 2)].p2_winner_from = None
                games_lower[2][math.floor(i / 2)].p2_loser_from = game.p1_loser_from


def single_elim(num_players):
    games_upper = generate_upper_bracket(num_players)
    add_players(num_players, games_upper)
    games_upper = add_bracket_ids_single_elim(games_upper)

    return games_upper


def double_elim(num_players, rematch):
    games_upper = generate_upper_bracket(num_players)
    games_lower = generate_lower_bracket(num_players)

    add_players(num_players, games_upper, games_lower)

    games_upper, games_lower = add_bracket_ids(games_upper, games_lower)

    grand_final = BracketGame(None)
    grand_final.p1_winner_from = games_upper[-1][-1].id_
    grand_final.p2_winner_from = games_lower[-1][-1].id_
    grand_final.id_ = 2*num_players - 2
    grand_final.bracket_id = games_lower[-1][-1].bracket_id + 1

    all_rounds = games_upper + games_lower + [[grand_final]]

    if rematch:
        grand_final_rematch = BracketGame(None)
        grand_final_rematch.p1_loser_from = grand_final.id_
        grand_final_rematch.p2_winner_from = grand_final.id_
        grand_final_rematch.id_ = 2*num_players - 1
        grand_final_rematch.bracket_id = grand_final.bracket_id + 1

        all_rounds += [[grand_final_rematch]]

    return all_rounds


def generate_bracket(player_list, tournament):
    stage = tournament.stages[0]
    num_players = len(player_list)

    if stage.format == 'single_elim':
        rounds = single_elim(num_players)
    else:
        rematch = stage.format == 'double_elim_rematch'
        rounds = double_elim(num_players, rematch)
 
    tournament_games = {}

    for bracket_round, stage_round in zip(rounds, stage.rounds):
        for bracket_game in bracket_round:
            # create game
            match_json = json.dumps({1: {1: {1: {'scores': [], 'double_missed': []},
                                         2: {'scores': [], 'double_missed': []}}}})

            game = Game(
                variant='x01',
                status='scheduled',
                type=stage_round.type_,
                in_mode=stage_round.in_mode,
                out_mode=stage_round.out_mode,
                bo_sets=stage_round.bo_sets,
                bo_legs=stage_round.bo_legs,
                two_clear_legs=stage_round.two_clear_legs,
                score_input_delay=stage_round.score_input_delay,
                tournament=tournament.hashid,
                p1_sets=0, p2_sets=0, p1_legs=0, p2_legs=0,
                p1_score=stage_round.type_, p2_score=stage_round.type_,
                match_json=match_json, begin=datetime.utcnow(),
                opponent_type='online', webcam=False,
            )
            game.player1 = player_list[bracket_game.p1-1] if bracket_game.p1 else None
            game.player2 = player_list[bracket_game.p2-1] if bracket_game.p2 else None

            game.p1_next_turn = stage_round.starter == 'me'
            if stage_round.starter == 'closest_to_bull':
                game.p1_next_turn = True
                closest_to_bull_json = json.dumps({1: [], 2: []})
                game.closest_to_bull_json = closest_to_bull_json
                game.closest_to_bull = True

            # create tournament game
            tournament_game = TournamentGame(
                game=game,
                tournament_stage_game_id=bracket_game.id_,
                tournament_stage_game_bracket_id=bracket_game.bracket_id,
            )
            p1_winner_from = tournament_games[bracket_game.p1_winner_from] if bracket_game.p1_winner_from else None
            p2_winner_from = tournament_games[bracket_game.p2_winner_from] if bracket_game.p2_winner_from else None
            p1_loser_from = tournament_games[bracket_game.p1_loser_from] if bracket_game.p1_loser_from else None
            p2_loser_from = tournament_games[bracket_game.p2_loser_from] if bracket_game.p2_loser_from else None
            
            tournament_games[bracket_game.id_] = tournament_game
            db.session.add(game)
            db.session.add(tournament_game)
            stage_round.games.append(tournament_game)
    tournament.status = 'started'
    db.session.commit()
