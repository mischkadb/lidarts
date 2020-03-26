from flask_babelex import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ChatmessageForm(FlaskForm):
    message = StringField('Message', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField(lazy_gettext('Submit message'))


class UserSearchForm(FlaskForm):
    username = StringField(lazy_gettext('Search user'), validators=[DataRequired(), Length(max=30)])
    submit = SubmitField(lazy_gettext('Search'))
