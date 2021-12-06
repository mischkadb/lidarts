#!/usr/bin/dumb-init /bin/sh
redis-server &
/app/docker/entry.sh
