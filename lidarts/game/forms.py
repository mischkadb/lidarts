from flask_babelex import _, lazy_gettext
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField, StringField, BooleanField
from wtforms.validators import DataRequired, InputRequired, NumberRange, ValidationError, Length

game_types = [('170', '170'), ('301', '301'), ('501', '501'), ('1001', '1001')]
opponents = [('local', lazy_gettext('Local')), ('online', 'Online'), ('computer', 'Computer')]
level = [(str(x), str(x)) for x in range(1, 10)]
starter = [('me', lazy_gettext('Me')), ('opponent', lazy_gettext('Opponent')),
           ('closest_to_bull', lazy_gettext('Closest to Bull'))]
bo_choice = [(str(x), str(x)) for x in range(1, 30)]
in_choice = [('si', 'Straight In'), ('di', 'Double In')]
out_choice = [('do', 'Double Out'), ('so', 'Single Out'), ('mo', 'Master Out')]


def impossible_numbers_check(form, field):
    impossible_numbers = [179, 178, 176, 175, 173, 172, 169]
    if field.data in impossible_numbers:
        raise ValidationError(lazy_gettext('Invalid number.'))


class ScoreForm(FlaskForm):
    score_value = IntegerField(lazy_gettext('Score'), validators=[InputRequired(),
                                                    NumberRange(min=0, max=180),
                                                    impossible_numbers_check])
    submit = SubmitField(lazy_gettext('Submit score'))


class CreateX01GameForm(FlaskForm):
    type = SelectField(lazy_gettext('Game type'), choices=game_types, validators=[DataRequired()])
    opponent = SelectField(lazy_gettext('Opponent'), default='online', choices=opponents, validators=[DataRequired()])
    opponent_name = StringField(lazy_gettext('Opponent name'))
    level = SelectField(lazy_gettext('Level'), choices=level)
    starter = SelectField(lazy_gettext('First to throw'), choices=starter, validators=[DataRequired()])
    bo_sets = SelectField(lazy_gettext('Best of Sets'), choices=bo_choice, validators=[DataRequired()])
    bo_legs = SelectField(lazy_gettext('Best of Legs'), choices=bo_choice, validators=[DataRequired()])
    two_clear_legs = BooleanField(lazy_gettext('Two Clear Legs'))
    in_mode = SelectField(lazy_gettext('Mode In'), choices=in_choice, validators=[DataRequired()])
    out_mode = SelectField(lazy_gettext('Mode Out'), choices=out_choice, validators=[DataRequired()])
    submit = SubmitField(lazy_gettext('Start game'))


class GameChatmessageForm(FlaskForm):
    message = StringField('Message', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField(lazy_gettext('Submit message'))
