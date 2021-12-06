FROM ubuntu:20.04

RUN mkdir /app 
WORKDIR /app

RUN apt-get update -y && \
    apt-get install -y git python3-pip python3-dev build-essential redis-server  dumb-init

COPY . /app
RUN chmod 755 /app/docker/entry.sh  /app/docker/dumb-init.sh

RUN pip install -r /app/requirements_dev.txt
RUN mkdir /app/instance
RUN cp example/config.py instance/config.py

RUN python3 manager.py createdb && \
    rm -r migrations && \
    flask db init && \
    flask db migrate && \
    flask db upgrade

RUN rm -rf /var/lib/apt/lists/* 

ENTRYPOINT [ "/app/docker/dumb-init.sh" ]

