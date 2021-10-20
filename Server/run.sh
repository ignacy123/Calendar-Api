#!/bin/bash
export FLASK_APP=./app/server.py
pipenv install
pipenv run flask run -h 0.0.0.0
