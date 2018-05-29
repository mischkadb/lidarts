from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ChatmessageForm(FlaskForm):
    message = StringField('Message', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Submit message')
