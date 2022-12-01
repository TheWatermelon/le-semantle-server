#!/bin/bash

APP_DIR=$(dirname $0)
source dataset.sh

[ -d ${APP_STORAGE} ]|| mkdir -p ${APP_STORAGE}

if [[ "$1" == "dev" ]]
then
    source ./venv/bin/activate

    export FLASK_DEBUG=1
    export FLASK_APP=lesemantleserver

    flask run --host=0.0.0.0
else # prod
    #gunicorn -b 0.0.0.0:$PORT lesemantleserver:app
    echo "Le mode production n'est pas disponible"
    echo "Le mode développement est accessible avec ./lesemantleserver.sh dev"
fi
