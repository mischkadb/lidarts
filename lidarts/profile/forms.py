from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

callers = [('default', 'Lidarts default'), ('DartCall 2007', 'DartCall 2007')]


class ChangeCallerForm(FlaskForm):
    callers = SelectField('Caller', choices=callers, validators=[DataRequired()])
    submit = SubmitField('Save')

