#!/bin/bash
set -e

server() {

  export HOST=${APP_HOST:-0.0.0.0}
  export PORT=${APP_PORT:-8080}
  export LOG_LEVEL=${LOG_LEVEL:-info}
  export MAX_WORKERS_NUM=${MAX_WORKERS_NUM:-1}

  exec uvicorn app.main:get_app --host ${HOST} --port ${PORT} \
  --workers ${MAX_WORKERS_NUM} --log-level ${LOG_LEVEL} --no-use-colors --no-access-log --factory

}

start-reload() {
  export HOST=${APP_HOST:-0.0.0.0}
  export PORT=${APP_PORT:-8000}
  exec uvicorn app.main:get_app --host ${HOST} --port ${PORT} --reload --factory
}

tests() {
  exec poetry run pytest
}


help() {
  echo "auth Docker."
  echo ""
  echo "Usage:"
  echo ""
  echo "server -- start auth backend"
  echo ""
}


case "$1" in
  server)
    shift
    server
    ;;
  help)
    shift
    help
    ;;
  tests)
    shift
    tests
    ;;
  start-reload)
    shift
    start-reload
    ;;
  *)
    exec "$@"
    ;;
esac
