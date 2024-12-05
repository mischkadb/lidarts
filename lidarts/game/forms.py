from flask_babelex import _, lazy_gettext
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField, StringField, BooleanField
from wtforms.validators import DataRequired, InputRequired, NumberRange, ValidationError, Length

game_types = [('170', '170'), ('301', '301'), ('501', '501'), ('701', '701'), ('1001', '1001')]
opponents = [('local', lazy_gettext('Local')), ('online', 'Online'), ('computer', 'Computer')]
level = [(str(x), str(x)) for x in range(1, 10)]
starter = [('me', lazy_gettext('Me')), ('opponent', lazy_gettext('Opponent')),
           ('closest_to_bull', lazy_gettext('Closest to Bull'))]
bo_choice = [(str(x), str(x)) for x in range(1, 30)]
first_to_choice = [(str(x), str(x)) for x in range(1, 30)]
x_legs_choice = [(str(x), str(x)) for x in range(1, 50)]
in_choice = [('si', 'Straight In'), ('di', 'Double In')]
out_choice = [('do', 'Double Out'), ('so', 'Straight Out'), ('mo', 'Master Out')]


def impossible_numbers_check(form, field):
    impossible_numbers = [179, 178, 176, 175, 173, 172, 169]
    if field.data in impossible_numbers:
        raise ValidationError(lazy_gettext('Invalid number.'))


class ScoreForm(FlaskForm):
    score_value = IntegerField(lazy_gettext('Score'), validators=[InputRequired(),
                                                    NumberRange(min=0, max=180),
                                                    impossible_numbers_check])
    submit = SubmitField(lazy_gettext('Submit score'))


class CricketScoreForm(FlaskForm):
    score_value = IntegerField(lazy_gettext('Score'), validators=[InputRequired(),
                                                    NumberRange(min=0, max=180),
                                                    impossible_numbers_check])
    submit = SubmitField(lazy_gettext('Submit score'))


class CreateGameForm(FlaskForm):
    goal_mode = SelectField(lazy_gettext('Goal mode'), choices=[('best_of', 'Best of'), ('first_to', 'First to'), ('x_legs', 'X Legs')], validators=[DataRequired()])
    bo_sets = SelectField(lazy_gettext('Best of Sets'), choices=bo_choice, validators=[DataRequired()])
    bo_legs = SelectField(lazy_gettext('Best of Legs'), choices=bo_choice, validators=[DataRequired()])
    first_to_sets = SelectField(lazy_gettext('First to Sets'), choices=first_to_choice, validators=[DataRequired()])
    first_to_legs = SelectField(lazy_gettext('First to Legs'), choices=first_to_choice, validators=[DataRequired()])
    x_legs = SelectField(lazy_gettext('How many legs?'), choices=x_legs_choice, validators=[DataRequired()])
    two_clear_legs = BooleanField(lazy_gettext('Two Clear Legs'))
    two_clear_legs_wc_mode = BooleanField(lazy_gettext('World Championship Mode'))
    starter = SelectField(lazy_gettext('First to throw'), choices=starter, validators=[DataRequired()])
    opponent = SelectField(lazy_gettext('Opponent'), default='online', choices=opponents, validators=[DataRequired()])
    opponent_name = StringField(lazy_gettext('Opponent name'))
    level = SelectField(lazy_gettext('Level'), choices=level)
    public_challenge = BooleanField(lazy_gettext('Public challenge'))
    webcam = BooleanField(lazy_gettext('Webcam game'))
    score_input_delay = IntegerField(lazy_gettext('Score input block'), default=0, validators=[NumberRange(min=0, max=15)])
    save_preset = BooleanField(lazy_gettext('Save settings'))
    tournament = SelectField(lazy_gettext('Tournament'), choices=[])
    submit = SubmitField(lazy_gettext('Start game'))


class CreateX01GameForm(CreateGameForm):
    type = SelectField(lazy_gettext('Game type'), choices=game_types, validators=[DataRequired()])
    in_mode = SelectField(lazy_gettext('Mode In'), choices=in_choice, validators=[DataRequired()])
    out_mode = SelectField(lazy_gettext('Mode Out'), choices=out_choice, validators=[DataRequired()])


class CreateCricketGameForm(CreateGameForm):
    pass


class GameChatmessageForm(FlaskForm):
    message = StringField('Message', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField(lazy_gettext('Submit message'))


class WebcamConsentForm(FlaskForm):
    webcam_consent = BooleanField(lazy_gettext('I have read the text above, understand the limitations and have a webcam setup to play.'), validators=[DataRequired()], default=False)
    stream_consent = BooleanField(lazy_gettext('(Optional) I allow my opponents to stream and record our game including my webcam video and audio.'), default=False)
    submit = SubmitField(lazy_gettext('Confirm'))
