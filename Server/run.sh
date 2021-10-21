#!/bin/bash
export FLASK_APP=./src/server.py
pipenv install
pipenv run flask run
