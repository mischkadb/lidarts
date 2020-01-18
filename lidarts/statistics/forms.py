from datetime import datetime
from flask_babelex import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DateField, SubmitField, HiddenField
from wtforms.widgets import html5
from wtforms.validators import DataRequired

opponents = [('all', lazy_gettext('All')), ('local', lazy_gettext('Local')),
             ('online', 'Online'), ('computer', 'Computer')]

computer_level = [('all', lazy_gettext('All')), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
                  ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')]

class StatisticsForm(FlaskForm):
    select_game_range_filter = SelectField('', choices=[('lastgames', lazy_gettext('Last ... games')),
                                                        ('daterange', lazy_gettext('From ... to ...'))])
    number_of_games = IntegerField(widget=html5.NumberInput(), default=50, validators=[DataRequired()])
    date_from = DateField(lazy_gettext('From'), widget=html5.DateInput(),
                          default=datetime(1901, 1, 1), validators=[DataRequired()])
    date_to = DateField(lazy_gettext('to'), widget=html5.DateInput(),
                        default=datetime(2099, 12, 31), validators=[DataRequired()])
    submit = SubmitField(lazy_gettext('Filter'))
    apply_filter = SubmitField(lazy_gettext('Apply'))
    hiddenfield_selected_tab = HiddenField(id='hiddenFieldSelectedTab')
    opponents = SelectField(lazy_gettext('Opponent'), id='selectOpponent', default='all', choices=opponents,
                            validators=[DataRequired()])
    computer_level = SelectField(lazy_gettext('Level'), default='all', choices=computer_level,
                                 validators=[DataRequired()])
    opponent_name = StringField(lazy_gettext('Opponent name'))
