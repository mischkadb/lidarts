class Statistics:
    """
    Class to store and calculate all statistics of a player
    """
    def __init__(self):
        self.scoring = {
            'ranges': {
                'under_20': 0,
                'over_20': 0,
                'over_40': 0,
                'over_40_19s': 0,
                'over_57': 0,
                'over_60': 0,
                'over_80': 0,
                'over_91': 0,
                'over_100': 0,
                'over_131': 0,
                'over_140': 0,
                'over_171': 0,
                '180': 0,
            },
            'percentages': {
                'under_20': 0,
                'over_20': 0,
                'over_40': 0,
                'over_40_19s': 0,
                'over_57': 0,
                'over_60': 0,
                'over_80': 0,
                'over_91': 0,
                'over_100': 0,
                'over_131': 0,
                'over_140': 0,
                'over_171': 0,
                '180': 0,
            },
        }
        self.finishing = {
            'ranges': {
                'range_2_40': 0,
                'range_41_80': 0,
                'range_81_100': 0,
                'range_101_120': 0,
                'range_121_140': 0,
                'range_141_170': 0,
            },
            'percentages': {
                'range_2_40': 0,
                'range_41_80': 0,
                'range_81_100': 0,
                'range_101_120': 0,
                'range_121_140': 0,
                'range_141_170': 0,
            },
        }
        self.games = {
            'record': {
                'wins': 0,
                'losses': 0,
                'draws': 0,
            },
            'percentages': {
                'wins': 0,
                'losses': 0,
                'draws': 0,
            },
        }
        self.first = {
            'scores': {
                'first3': [],
                'first6': [],
                'first9': [],
            },
            'averages': {
                'first3': 0,
                'first6': 0,
                'first9': 0,
            },
        }
        self.darts_thrown = 0
        self.double_thrown = 0
        self.legs_won = 0
        self.total_score = 0
        self.average = 0
        self.first9_scores = []
        self.first9_average = 0
        self.doubles = 0
        self.number_of_games = 0
        self.shortest_leg = 0
        self.number_of_legs = 0
        self.legs_lost = 0
        self.first6_scores = []
        self.first6_average = 0
        self.first3_scores = []
        self.first3_average = 0
        self.legs_won_percent = 0
        self.legs_lost_percent = 0
        self.number_of_rounds = 0
        self.highest_finish = 0
        

    def to_dict(self):
        return {
            'scoring': self.scoring,
            'finishing': self.finishing,
            'games': self.games,
            'first': {
                'scores': {
                    'first3': list(self.first['scores']['first3']),
                    'first6': list(self.first['scores']['first6']),
                    'first9': list(self.first['scores']['first9']),
                },
                'averages': self.first['averages']
            },
            'darts_thrown': self.darts_thrown,
            'double_thrown': self.double_thrown,
            'legs_won': self.legs_won,
            'total_score': self.total_score,
            'average': self.average,
            'first9_scores': list(self.first9_scores),
            'first9_average': self.first9_average,
            'doubles': self.doubles,
            'number_of_games': self.number_of_games,
            'shortest_leg': self.shortest_leg,
            'number_of_legs': self.number_of_legs,
            'legs_lost': self.legs_lost,
            'first6_scores': list(self.first6_scores),
            'first6_average': self.first6_average,
            'first3_scores': list(self.first3_scores),
            'first3_average': self.first3_average,
            'legs_won_percent': self.legs_won_percent,
            'legs_lost_percent': self.legs_lost_percent,
            'number_of_rounds': self.number_of_rounds,
            'highest_finish': self.highest_finish
        }
