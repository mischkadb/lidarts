from flask_babelex import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange

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
    submit = SubmitField(lazy_gettext('Save'))
