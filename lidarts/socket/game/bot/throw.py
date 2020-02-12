# -*- coding: utf-8 -*-

"""Simulate a computer player dart throw and calculate the score."""

from collections import deque

import numpy as np

NUM_SEGMENTS = 20
SINGLE = 'S'
DOUBLE = 'D'
TRIPLE = 'T'
SINGLE_BULL = 'S25'
DOUBLE_BULL = 'D25'
# cyclic data structure to represent the outer dartboard segments


def _get_bullseye_possible_hits(target, computer):
    possible_hits = {}
    if target == DOUBLE_BULL:
        # probabilities for double bull
        possible_hits[DOUBLE_BULL] = computer['hit_chance_D25'][0]
        possible_hits[SINGLE_BULL] = computer['hit_chance_D25'][1]
        # all numbers have a basic chance to be hit
        for segment in range(1, NUM_SEGMENTS + 1):
            field = f'S{segment}'
            possible_hits[field] = computer['hit_chance_D25'][2]
    elif target == SINGLE_BULL:
        # probabilities for single bull
        possible_hits[DOUBLE_BULL] = computer['hit_chance_S25'][0]
        possible_hits[SINGLE_BULL] = computer['hit_chance_S25'][1]
        # all numbers have a basic chance to be hit
        for outer_segment in range(1, NUM_SEGMENTS + 1):
            field = f'{SINGLE}{outer_segment}'
            possible_hits[field] = computer['hit_chance_S25'][2]

    return possible_hits


def _simulate_throw(field_type, target_numbers, computer):
    # probability to hit: target / number left / number right
    if field_type == DOUBLE:
        return str(np.random.choice(target_numbers, p=computer['hit_chance_field_at_double']))
    return str(np.random.choice(target_numbers, p=computer['hit_chance_field']))


def _get_outer_possible_hits(target, computer, field_type):
    # probabilities to hit: 0 / single / double / triple
    if field_type == SINGLE:
        hit_chance = computer['hit_chance_single']
    elif field_type == DOUBLE:
        hit_chance = computer['hit_chance_double']
    else:
        hit_chance = computer['hit_chance_triple']

    dartboard = deque([20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5])  # noqa: WPS221
    # target number
    target_numbers = [int(target[1:])]

    # get numbers next to target
    dartboard.rotate(-dartboard.index(int(target[1:])))
    target_numbers.append(dartboard[-1])
    target_numbers.append(dartboard[1])

    number_hit = _simulate_throw(field_type, target_numbers, computer)

    possible_hits = {}
    possible_hits['0'] = hit_chance[0]
    possible_hits[f'{SINGLE}{number_hit}'] = hit_chance[1]
    possible_hits[f'{DOUBLE}{number_hit}'] = hit_chance[2]
    possible_hits[f'{TRIPLE}{number_hit}'] = hit_chance[3]

    return possible_hits


def throw_dart(target, computer):
    """Simulate a CPU dart throw.

    Args:
        target: Targeted segment
        computer: CPU player level

    Returns:
        Score of hit segment and the hit segment itself
    """
    if target in {DOUBLE_BULL, SINGLE_BULL}:
        possible_hits = _get_bullseye_possible_hits(target, computer)
    else:
        field_type = target[0]  # 'S', 'D' or 'T'
        possible_hits = _get_outer_possible_hits(target, computer, field_type)

    hit = np.random.choice(list(possible_hits), p=list(possible_hits.values()))

    if hit == '0':
        return 0, '0'
    elif hit[0] == SINGLE:
        factor = 1
    elif hit[0] == DOUBLE:
        factor = 2
    else:
        factor = 3

    number = int(hit[1:])
    return number * factor, hit
