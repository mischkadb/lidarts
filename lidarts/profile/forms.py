from flask import url_for
from flask_babelex import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange
import json

with open('lidarts/static/countries.json') as countries_file:
    countries = sorted(json.load(countries_file).items(), key=lambda k: k[1])
    countries.insert(0, ['None', 'None'])

callers = [('default', 'Lidarts default'), ('DartCall 2007', 'DartCall 2007'), ('lidartsUK', 'Lidarts UK')]
enabled_disabled = [('enabled', lazy_gettext('Enabled')), ('disabled', lazy_gettext('Disabled'))]


class ChangeCallerForm(FlaskForm):
    callers = SelectField(lazy_gettext('Caller'), choices=callers, validators=[DataRequired()])
    submit = SubmitField(lazy_gettext('Save'))


class ChangeCPUDelayForm(FlaskForm):
    delay = IntegerField(lazy_gettext('Trainer delay'), validators=[DataRequired(), NumberRange(0, 30)])
    submit = SubmitField(lazy_gettext('Save'))


class GeneralSettingsForm(FlaskForm):
    notification_sound = SelectField(
        lazy_gettext('Notification sound'),
        choices=enabled_disabled,
        validators=[DataRequired()],
    )

    allow_challenges = SelectField(
        lazy_gettext('Allow challenges'),
        choices=enabled_disabled,
        validators=[DataRequired()],
    )

    allow_private_messages = SelectField(
        lazy_gettext('Allow private messages'),
        choices=enabled_disabled,
        validators=[DataRequired()],
    )

    allow_friend_requests = SelectField(
        lazy_gettext('Allow friend requests'),
        choices=enabled_disabled,
        validators=[DataRequired()],
    )

    country = SelectField(
        lazy_gettext('Country'),
        choices=countries,
        validators=[DataRequired()],
    )

    submit = SubmitField(lazy_gettext('Save'))
