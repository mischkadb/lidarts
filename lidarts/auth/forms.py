from wtforms import StringField, validators
from wtforms.validators import DataRequired, ValidationError
from lidarts.models import User
from flask_security import LoginForm
from flask_security.forms import Form, PasswordConfirmFormMixin, NextFormMixin,\
    RegisterFormMixin, UniqueEmailFormMixin, NewPasswordFormMixin, ValidatorMixin
from flask_babel import _, lazy_gettext


class Required(ValidatorMixin, validators.DataRequired):
    pass


class Length(ValidatorMixin, validators.Length):
    pass


username_required = Required('Username is required')
username_validator = Length(min=3, max=20)


def unique_username(form, field):
    user = User.query.filter(User.username.ilike(field.data)).first()
    if user is not None:
        raise ValidationError('Username is already taken')


class UniqueUsernameFormMixin():
    username = StringField(
        'Username',
        validators=[username_required, username_validator, unique_username])


class ExtendedConfirmRegisterForm(Form, RegisterFormMixin,
                          UniqueEmailFormMixin, NewPasswordFormMixin, UniqueUsernameFormMixin):
    pass


class ExtendedRegisterForm(ExtendedConfirmRegisterForm, PasswordConfirmFormMixin, NextFormMixin):
    pass


class ExtendedLoginForm(LoginForm):
    # hacked in username to use default email validation from flask-security
    email = StringField(lazy_gettext('Username or Email Address'), validators=[DataRequired()])






