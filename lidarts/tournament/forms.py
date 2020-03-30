from flask_babelex import _, lazy_gettext
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, TextAreaField
from wtforms_components import TimeField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length


class CreateTournamentForm(FlaskForm):
    name = StringField(lazy_gettext('Tournament name'),  validators=[DataRequired(), Length(min=3, max=50)])
    description = TextAreaField(lazy_gettext('Description'), validators=[Length(min=0, max=1000)])
    public_tournament = BooleanField(lazy_gettext('Open to the public'))
    external_link = StringField(lazy_gettext('External link'), validators=[Length(min=0, max=120)])
    start_date = DateField('Start date', format='%Y-%m-%d')
    start_time = TimeField('Start time')
    submit = SubmitField(lazy_gettext('Create Tournament'))
