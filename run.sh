#!/bin/bash

COMMIT_ID=$(git rev-parse --short HEAD)
COMMIT_ID=$COMMIT_ID docker-compose -f docker-compose.yml up -d
PORT=${1:-8000}
python3 manage.py makemigrations --no-input
python3 manage.py migrate --no-input
# python3 manage.py load_sources  #  Load News-Sources
python3 manage.py runserver 0.0.0.0:$PORT