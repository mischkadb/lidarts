[lidarts.org](https://lidarts.org)
----

Lidarts is a free/libre, open-source online darts scoring website.

The project is mostly written in [Python3](https://www.python.org). 
The backend is based on [Flask-Socketio](https://flask-socketio.readthedocs.io/en/latest/). 
[gevent](http://www.gevent.org/) workers are managed by [gunicorn](https://gunicorn.org/) 
and communicate over [redis](https://redis.io/). 
Data is stored in a [PostgresSQL](https://www.postgresql.org/) database.
HTTP requests and WebSockets are proxied by [nginx](https://www.nginx.com/).

The entire project is driven by volunteers. Everyone is invited to contribute. 
Join us on our [Discord server](https://discordapp.com/invite/devMXxf)!

Installation
----

To set up a development environment make sure you have Python 3.7 or later installed 
and a PostgreSQL database running on your localhost.

Clone the repo
~~~
git clone https://github.com/mischkadb/lidarts lidarts-dev
~~~

Create a new virtual environment and activate it
~~~
cd lidarts-dev
python3.7 -m venv venv
source venv/bin/activate
~~~

Install dependencies
~~~
pip install -r requirements.txt
~~~

Create instance folder and copy example config
~~~
mkdir instance
cp example/config.py instance/config.py
~~~

Initialize the migration directory and the database tables
~~~
flask db init
flask db migrate
flask db upgrade
~~~

Run the development server with
~~~
python run.py
~~~
