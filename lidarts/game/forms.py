from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField, StringField
from wtforms.validators import DataRequired, InputRequired, NumberRange, ValidationError

game_types = [('170', '170'), ('301', '301'), ('501', '501'), ('1001', '1001')]
opponents = [('local', 'Local'), ('online', 'Online'), ('computer', 'Computer')]
level = [(str(x), str(x)) for x in range(1, 10)]
starter = [('me', 'Me'), ('opponent', 'Opponent'), ('closest_to_bull', 'Closest to Bull')]
bo_choice = [(str(x), str(x)) for x in range(1, 30)]
in_choice = [('si', 'Straight In'), ('di', 'Double In')]
out_choice = [('do', 'Double Out'), ('so', 'Single Out'), ('mo', 'Master Out')]


def impossible_numbers_check(form, field):
    impossible_numbers = [179, 178, 176, 175, 173, 172, 169]
    if field.data in impossible_numbers:
        raise ValidationError('Invalid number.')


class ScoreForm(FlaskForm):
    score_value = IntegerField('Score', validators=[InputRequired(),
                                                    NumberRange(min=0, max=180),
                                                    impossible_numbers_check])
    submit = SubmitField('Submit score')


class CreateX01GameForm(FlaskForm):
    type = SelectField('Game type', choices=game_types, validators=[DataRequired()])
    opponent = SelectField('Opponent', default='online', choices=opponents, validators=[DataRequired()])
    opponent_name = StringField('Opponent name')
    level = SelectField('Level', choices=level)
    starter = SelectField('First to throw', choices=starter, validators=[DataRequired()])
    bo_sets = SelectField('Best of Sets', choices=bo_choice, validators=[DataRequired()])
    bo_legs = SelectField('Best of Legs', choices=bo_choice, validators=[DataRequired()])
    in_mode = SelectField('Mode In', choices=in_choice, validators=[DataRequired()])
    out_mode = SelectField('Mode Out', choices=out_choice, validators=[DataRequired()])
    submit = SubmitField('Start game')

