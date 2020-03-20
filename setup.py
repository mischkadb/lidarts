from setuptools import find_packages, setup
from instance.config import VERSION

setup(
    name='lidarts',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'alembic',
        'bcrypt',
        'bleach',
        'coverage',
        'Flask-BabelEx',
        'Flask-Login',
        'Flask-Mail',
        'Flask-Migrate',
        'Flask-Moment',
        'Flask-Security',
        'Flask-SocketIO',
        'Flask-SQLAlchemy',
        'Flask-Uploads',
        'Flask-WTF',
        'gevent',
        'gunicorn',
        'numpy',
        'psycopg2-binary',
        'pytest',
        'python-dotenv',
        'redis'
    ],
)
