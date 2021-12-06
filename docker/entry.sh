#!/bin/bash
CONFIG="/app/instance/config.py"
GUNICORN_PORT=5000
GUNICORN_WORKERS=2
GUNICORN_THREADS=2

#Generate a unique secret key for flask
SECRET_KEY=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1)
sed -i "s/change-me/${SECRET_KEY}/" ${CONFIG}

if [ -n "${WEBSERVER_PORT}" ]; then
    GUNICORN_PORT=${WEBSERVER_PORT}
fi

if [ -n "${WEBSERVER_WORKERS}" ]; then
    GUNICORN_WORKERS=${WEBSERVER_WORKERS}
fi

if [ -n "${WEBSERVER_THREADS}" ]; then
    GUNICORN_THREADS=${WEBSERVER_THREADS}
fi

gunicorn  --chdir /app -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker --threads ${GUNICORN_THREADS} "lidarts:create_app()" -b 0.0.0.0:${GUNICORN_PORT}
