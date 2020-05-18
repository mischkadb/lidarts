from flask_babelex import _, lazy_gettext
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, TextAreaField, RadioField, SelectField, FormField, FieldList, IntegerField
from wtforms_components import TimeField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from lidarts.game.forms import game_types, starter, bo_choice, in_choice, out_choice


tournament_formats = [
    ('single_elim', lazy_gettext('Single-elimination')),
    ('double_elim_rematch', lazy_gettext('Double-elimination (Rematch in Grand Final)')),
    ('double_elim_no_rematch', lazy_gettext('Double-elimination (No rematch in Grand Final)')),
]


class RequiredIf(DataRequired):
    # a validator which makes a field required if
    # another field is set and has a truthy value

    field_flags = ('requiredif',)

    def __init__(self, other_field_name, message=None, *args, **kwargs):
        self.other_field_name = other_field_name
        self.message = message

    def __call__(self, form, field):
        other_field = form[self.other_field_name]
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)
        else:
            Optional().__call__(form, field)


class CreateTournamentForm(FlaskForm):
    name = StringField(lazy_gettext('Tournament name'),  validators=[DataRequired(), Length(min=3, max=50)])
    description = TextAreaField(lazy_gettext('Description'), validators=[Length(min=0, max=1000)])
    automatic_management = BooleanField(lazy_gettext('Use Lidarts to manage tournament brackets'))
    public_tournament = BooleanField(lazy_gettext('Open to the public'))
    registration_open = BooleanField(lazy_gettext('Player registration is open'))
    registration_apply = BooleanField(lazy_gettext('Organiser needs to confirm new players'))
    external_url = StringField(lazy_gettext('External URL'), validators=[RequiredIf('public_tournament'), Length(min=1, max=120)])
    start_date = DateField('Start date', format='%Y-%m-%d', validators=[RequiredIf('public_tournament')])
    start_time = TimeField('Start time', validators=[RequiredIf('public_tournament')])
    tournament_format = SelectField(
        lazy_gettext('Tournament format'),
        choices=tournament_formats,
        default='single_elim',
    )
    submit = SubmitField(lazy_gettext('Create Tournament'))
    submit_save = SubmitField(lazy_gettext('Save settings'))


class ConfirmStreamGameForm(FlaskForm):
    games = RadioField(lazy_gettext('Streamable games'), validators=[DataRequired()])
    submit = SubmitField(lazy_gettext('Select game'))


class CloseRegistrationForm(FlaskForm):
    submit = SubmitField(lazy_gettext('Continue'))


class RoundForm(FlaskForm):
    name_ = StringField()
    bo_sets = SelectField(lazy_gettext('Best of Sets'), choices=bo_choice, validators=[DataRequired()])
    bo_legs = SelectField(lazy_gettext('Best of Legs'), choices=bo_choice, validators=[DataRequired()])
    two_clear_legs = BooleanField(lazy_gettext('Two Clear Legs'))
    starter = SelectField(lazy_gettext('First to throw'), choices=starter, validators=[DataRequired()])
    score_input_delay = IntegerField(lazy_gettext('Score input block'), default=0, validators=[NumberRange(min=0, max=15)])
    type_ = SelectField(lazy_gettext('Game type'), choices=game_types, validators=[DataRequired()])
    in_mode = SelectField(lazy_gettext('Mode In'), choices=in_choice, validators=[DataRequired()])
    out_mode = SelectField(lazy_gettext('Mode Out'), choices=out_choice, validators=[DataRequired()])


class TournamentPreparationForm(FlaskForm):
    player_list = StringField('Player List', validators=[DataRequired()])
    rounds = FieldList(FormField(RoundForm), min_entries=1)
    submit = SubmitField(lazy_gettext('Continue'))
