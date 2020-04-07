import os
basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'change-me'
# SQLALCHEMY_DATABASE_URI = 'postgres:///lidarts')
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'lidarts.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True
SECURITY_USER_IDENTITY_ATTRIBUTES = ('username', 'email')
SECURITY_PASSWORD_SALT = 'change-me'
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_EMAIL_SENDER = 'noreply@lidarts.org'

MAIL_SERVER = 'mailserver.com'
MAIL_PORT = 587
MAIL_USERNAME = 'username'
MAIL_PASSWORD = 'password'
MAIL_USE_TLS = True
MAIL_USE_SSL = False

UPLOADS_DEFAULT_DEST = 'static/'
UPLOADS_DEFAULT_URL = '/static/'
UPLOADED_FILES_DENY = ['svg', 'webp']

VERSION = '0.6.2-13'

DEBUG = True
