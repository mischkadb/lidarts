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
        'Flask-MonitoringDashboard',
        'Flask-Script',
        'Flask-Security',
        'Flask-SocketIO',
        'Flask-SQLAlchemy',
        # Flask-Uploads 0.2.1 is not compatible with werkzeug 1.0.0
        'Flask-Uploads @ https://github.com/maxcountryman/flask-uploads/archive/f66d7dc93e684fa0a3a4350a38e41ae00483a796.zip#egg=Flask-Uploads-0.2.2.dev',
        'Flask-WTF',
        'gevent',
        'gunicorn',
        'numpy',
        'psycopg2-binary',
        'pytest',
        'python-dotenv',
        'redis',
        'rq',
    ],
)
