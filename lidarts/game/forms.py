from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError

game_types = [('170', '170'), ('301', '301'), ('501', '501')]
opponents = [('computer', 'Computer'), ('user', 'User')]
starter = [('me', 'Me'), ('opoonent', 'Opponent'), ('clostest', 'Closest to Bullseye')]
bo_choice = [(str(x), str(x)) for x in range(1, 30)]


def bogey_check(form, field):
    bogey_numbers = [179, 178, 176, 175, 173, 172, 169]
    if field.data in bogey_numbers:
        raise ValidationError('Bogey number.')


class ScoreForm(FlaskForm):
    score_value = IntegerField('Score', validators=[DataRequired(), NumberRange(min=0, max=180), bogey_check])
    submit = SubmitField('Submit score')


class CreateX01GameForm(FlaskForm):
    type = SelectField('Game type', choices=game_types, validators=[DataRequired()])
    opponent = SelectField('Opponent', choices=opponents, validators=[DataRequired()])
    starter = SelectField('First to throw', choices=starter, validators=[DataRequired()])
    bo_sets = SelectField('Best of Sets', choices=bo_choice, validators=[DataRequired()])
    bo_legs = SelectField('Best of Legs', choices=bo_choice, validators=[DataRequired()])
    submit = SubmitField('Start game')

