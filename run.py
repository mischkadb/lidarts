# -*- coding: utf-8 -*-

"""Run flask-socketio app locally.

Flask-Socketio replaces the standard way of Flask to initialize
a development server with socketio.run().

Run this file to start a local development server correctly.
"""

from lidarts import create_app, socketio

app = create_app()

if __name__ == '__main__':
    port = 5000
    socketio.run(app, host='127.0.0.1', port=port, log_output=True)
