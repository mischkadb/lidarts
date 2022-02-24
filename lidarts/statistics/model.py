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
