from wtforms import StringField, PasswordField, validators
from wtforms.validators import DataRequired, ValidationError
from lidarts.models import User
from flask_security import LoginForm
from flask_security.forms import Form, PasswordConfirmFormMixin, NextFormMixin, \
    RegisterFormMixin, UniqueEmailFormMixin, NewPasswordFormMixin, ValidatorMixin
from flask_babel import _, lazy_gettext


class Required(ValidatorMixin, validators.DataRequired):
    pass


class Length(ValidatorMixin, validators.Length):
    pass


password_required = Required(message='PASSWORD_NOT_PROVIDED')
password_length = Length(min=8, max=128, message='Password must have at least 8 characters')

username_required = Required('Username is required')
username_validator = Length(min=3, max=25)


def valid_password(form, field):
    # password policy: either length > 15 or length > 8 and at least two out of: lowercase, uppercase, number, symbol
    password = field.data
    features = 0
    if len(password) >= 15:
        features += 2
    if any(x.isupper() for x in password):
        features += 1
    if any(x.islower() for x in password):
        features += 1
    if any(x.isdigit() for x in password):
        features += 1
    if any(not x.isalnum() for x in password):
        features += 1

    if features < 2:
        raise ValidationError('Password must have at least 15 characters OR contain at least two out of these: '
                              'lowercase letter, uppercase letter, number, symbol.')


def unique_username(form, field):
    user = User.query.filter(User.username.ilike(field.data)).first()
    if user is not None:
        raise ValidationError('Username is already taken')


def valid_username(form, field):
    username = field.data
    if not username[0].isalnum() and username[0] not in '[(':
        raise ValidationError('Username must start with a letter, number or "(["')
    if not username[-1].isalnum():
        raise ValidationError('Username must end with a letter or a number')
    last_is_symbol = False
    for x in username:
        if not x.isalnum() and x not in ' .-_()[]':
            raise ValidationError('Username contains invalid symbols.')
        if (not x.isalnum() and x not in '([') and last_is_symbol:
            raise ValidationError('Two special characters in a row are not allowed.')
        last_is_symbol = not x.isalnum()


class UniqueUsernameFormMixin():
    username = StringField(
        'Username',
        validators=[username_required, username_validator, unique_username, valid_username])


class ExtendedConfirmRegisterForm(Form, RegisterFormMixin,
                                  UniqueEmailFormMixin, NewPasswordFormMixin, UniqueUsernameFormMixin):
    pass


class ExtendedRegisterForm(ExtendedConfirmRegisterForm, PasswordConfirmFormMixin, NextFormMixin):
    password = PasswordField('Password', validators=[password_required, password_length, valid_password])


class ExtendedLoginForm(LoginForm):
    # hacked in username to use default email validation from flask-security
    email = StringField(lazy_gettext('Username or Email Address'), validators=[DataRequired()])






