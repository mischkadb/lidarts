from flask_babelex import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import SubmitField, DecimalField
from wtforms.validators import DataRequired


class BoardCoordinateForm(FlaskForm):
    x1 = DecimalField('x1', validators=[DataRequired()])
    y1 = DecimalField('y1', validators=[DataRequired()])
    x2 = DecimalField('x2', validators=[DataRequired()])
    y2 = DecimalField('y2', validators=[DataRequired()])
    x3 = DecimalField('x3', validators=[DataRequired()])
    y3 = DecimalField('y3', validators=[DataRequired()])
    submit = SubmitField(lazy_gettext('Submit'))

