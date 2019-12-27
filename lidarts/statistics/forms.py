from flask_babelex import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import validators, SelectField, IntegerField, DateField, SubmitField
from wtforms.widgets import html5
from datetime import datetime

class StatisticsForm(FlaskForm):
    selectGameRangeFilter = SelectField('', choices=[('lastgames',lazy_gettext('Last ... games')),('daterange',lazy_gettext('From ... to ...'))])
    numberOfGames = IntegerField(widget=html5.NumberInput(), default=50, validators=[validators.DataRequired()])
    dateFrom = DateField(lazy_gettext('From'), widget=html5.DateInput(), default=datetime(1901, 1, 1), validators=[validators.DataRequired()])
    dateTo = DateField(lazy_gettext('to'), widget=html5.DateInput(), default=datetime(2099, 12, 31), validators=[validators.DataRequired()])
    submit = SubmitField(lazy_gettext('Filter'))

