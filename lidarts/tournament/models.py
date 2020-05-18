class BracketGame:
    winner = None
    loser = None
    p1_winner_from = None
    p2_winner_from = None
    p1_loser_from = None
    p2_loser_from = None
    bracket_id = None

    def __init__(self, id_, p1=None, p2=None):
        self.id_ = id_
        self.p1 = p1
        self.p2 = p2


    def __repr__(self):
        if self.p1:
            p1 = self.p1
        elif self.p1_winner_from:
            p1 = f'w{self.p1_winner_from}'
        elif self.p1_loser_from:
            p1 = f'l{self.p1_loser_from}'
        else:
            p1 = '-'

        if self.p2:
            p2 = self.p2
        elif self.p2_winner_from:
            p2 = f'w{self.p2_winner_from}'
        elif self.p2_loser_from:
            p2 = f'l{self.p2_loser_from}'
        else:
            p2 = '-'

        id_ = self.id_
        id_ = f'{id_}/b{self.bracket_id}' if self.bracket_id else id_
        return f'{id_}: {p1} v {p2}'


