from wtforms import BooleanField, StringField, PasswordField, validators
from wtforms.validators import DataRequired, ValidationError
from lidarts.models import User
from flask_security import LoginForm
from flask_security.forms import Form, PasswordConfirmFormMixin, NextFormMixin, \
    RegisterFormMixin, UniqueEmailFormMixin, NewPasswordFormMixin, ValidatorMixin, \
    ChangePasswordForm, ResetPasswordForm, ConfirmRegisterForm
from flask_babelex import _, lazy_gettext
from sqlalchemy import func


class Required(ValidatorMixin, validators.DataRequired):
    pass


class Length(ValidatorMixin, validators.Length):
    pass


password_required = Required(message='PASSWORD_NOT_PROVIDED')
password_length = Length(min=8, max=128, message=lazy_gettext('Password must have at least 8 characters'))

username_required = Required(lazy_gettext('Username is required'))
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
        raise ValidationError(lazy_gettext('Password must have at least 15 characters OR contain at least two out of '
                                           'these: lowercase letter, uppercase letter, number, symbol.'))


def unique_username(form, field):
    user = User.query.filter(func.lower(User.username) == func.lower(field.data)).first()
    if user is not None:
        raise ValidationError(lazy_gettext('Username is already taken'))


def valid_username(form, field):
    username = field.data
    if not username[0].isalnum() and username[0] not in '[(':
        raise ValidationError(lazy_gettext('Username must start with a letter, number or "(["'))
    if not username[-1].isalnum() and username[-1] not in ')]':
        raise ValidationError(lazy_gettext('Username must end with a letter or a number or ")]"'))
    last_is_symbol = False
    for x in username:
        if not x.isalnum() and x not in ' .-_()[]':
            raise ValidationError(lazy_gettext('Username contains invalid symbols.'))
        if (not x.isalnum() and x not in '([') and last_is_symbol:
            raise ValidationError(lazy_gettext('Two special characters in a row are not allowed.'))
        last_is_symbol = not x.isalnum()


class UniqueUsernameFormMixin():
    username = StringField(
        lazy_gettext('Username'),
        validators=[username_required, username_validator, unique_username, valid_username])


class ExtendedConfirmRegisterForm(Form, RegisterFormMixin,
                                  UniqueEmailFormMixin, NewPasswordFormMixin, UniqueUsernameFormMixin):
    pass


class ExtendedRegisterForm(ExtendedConfirmRegisterForm, PasswordConfirmFormMixin, NextFormMixin):
    password = PasswordField(lazy_gettext('Password'), validators=[password_required, password_length, valid_password])


class ExtendedLoginForm(LoginForm):
    # hacked in username to use default email validation from flask-security
    email = StringField(lazy_gettext('Username or Email Address'), validators=[DataRequired()])


class ExtendedChangePasswordForm(ChangePasswordForm):
    new_password = PasswordField(lazy_gettext('Password'), validators=[password_required, password_length, valid_password])


class ExtendedResetPasswordForm(ResetPasswordForm):
    password = PasswordField(lazy_gettext('Password'), validators=[password_required, password_length, valid_password])


class ChangeUsernameForm(Form, UniqueUsernameFormMixin):
    confirmation = BooleanField(lazy_gettext('Accept'), validators=[DataRequired()])