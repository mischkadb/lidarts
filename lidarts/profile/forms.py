from flask import url_for
from flask_babelex import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from lidarts.profile.countries import COUNTRIES

callers = [('default', 'Lidarts default'), ('mischka', 'Lidarts mischka'), ('DartCall 2007', 'DartCall 2007')]
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

    checkout_suggestions = SelectField(
        lazy_gettext('Checkout suggestions'),
        choices=enabled_disabled,
        validators=[DataRequired()],
    )

    show_average_in_chat_list = SelectField(
        lazy_gettext('Show averages in user list'),
        choices=enabled_disabled,
        validators=[DataRequired()],
    )

    submit = SubmitField(lazy_gettext('Save'))


class ChangeCountryForm(FlaskForm):
    country = SelectField(
        lazy_gettext('Country'),
        choices=COUNTRIES,
        validators=[DataRequired()],
    )

    accept_country_cooldown = BooleanField(lazy_gettext('Accept'), validators=[DataRequired()])

    submit = SubmitField(lazy_gettext('Save'))
