from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange

callers = [('default', 'Lidarts default'), ('DartCall 2007', 'DartCall 2007'), ('lidartsUK', 'Lidarts UK')]


class ChangeCallerForm(FlaskForm):
    callers = SelectField('Caller', choices=callers, validators=[DataRequired()])
    submit = SubmitField('Save')


class ChangeCPUDelayForm(FlaskForm):
    delay = IntegerField('CPU delay', validators=[DataRequired(), NumberRange(0, 30)])
    submit = SubmitField('Save')

