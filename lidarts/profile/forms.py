from flask import url_for
from flask_babelex import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, SubmitField, IntegerField, TextAreaField, StringField
from wtforms.validators import DataRequired, NumberRange, Length, Regexp
from lidarts.profile.countries import COUNTRIES

enabled_disabled = [('enabled', lazy_gettext('Enabled')), ('disabled', lazy_gettext('Disabled'))]


class EditProfileForm(FlaskForm):
    bio = TextAreaField(lazy_gettext('Description'), validators=[Length(min=0, max=2000)])
    submit = SubmitField(lazy_gettext('Save'))


class ChangeCallerForm(FlaskForm):
    callers = SelectField(lazy_gettext('Caller'), validators=[DataRequired()])
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


class WebcamSettingsForm(FlaskForm):
    activated = SelectField(
        lazy_gettext('Webcam activated'),
        choices=enabled_disabled,
        validators=[DataRequired()],
    )

    stream_consent = SelectField(
        lazy_gettext('Allow streaming'),
        choices=enabled_disabled,
        validators=[DataRequired()],
    )

    mobile_app = SelectField(
        lazy_gettext('Use Jitsi mobile app'),
        choices=enabled_disabled,
        validators=[DataRequired()],
    )

    mobile_follower_mode = SelectField(
        lazy_gettext('Mobile follow mode'),
        choices=enabled_disabled,
        validators=[DataRequired()],
    )

    force_scoreboard_page = SelectField(
        lazy_gettext('Show only scoreboard on main device'),
        choices=enabled_disabled,
        validators=[DataRequired()],
    )

    jitsi_public_server = BooleanField(lazy_gettext('Use public Jitsi server'))

    submit = SubmitField(lazy_gettext('Save'))


class LivestreamSettingsForm(FlaskForm):
    channel_id = StringField(lazy_gettext('Channel ID'), validators=[Length(min=15, max=30), Regexp('^UC\w+$')])
    submit = SubmitField(lazy_gettext('Save'))