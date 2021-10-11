#!/bin/python3

import flask 
from flask import request, jsonify
import json
import datetime
import database
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/userinfo.email', 'openid']


app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/lall', methods=['GET'])
def list_all():
    return jsonify(database.all_activities())

@app.route('/fav', methods=['GET', 'PUT', 'DELETE'])
def fav():
    if 'credentials' not in request.args:
        return "Please provide a Google Authentication token.", 400
    if 'name' not in request.args and (flask.request.method == 'PUT' or flask.request.method == 'DELETE'):
        return "Please provide a name.", 400
    
    email = get_email_from_json_credentials(json.loads(request.args['credentials']))
    
    if request.method == 'GET':
        return jsonify(database.fav_activities(email))
    if request.method == 'PUT':
        name = request.args['name']
        database.new_fav(email, name)
        return jsonify([name]), 200
    if request.method == 'DELETE':
        name = request.args['name']
        database.delete_fav(email, name)
        return jsonify([name]), 200
    
@app.route('/event', methods=['PUT'])
def event():
    if 'credentials' not in request.args:
        return "Please provide a Google Authentication token.", 400
    if 'start_date' not in request.args:
        return "Please choose a start_date.", 400
    if 'end_date' not in request.args:
        return "Please choose an end_date.", 400
    if 'name' not in request.args and request.method == 'PUT':
        return "Please specify an activity.", 400
    
    if request.method == 'PUT':
        return request.args, 200
    
@app.route('/email', methods=['GET'])
def email():
    if 'credentials' not in request.args:
        return "Please provide a Google Authentication token.", 400
    try:
        email = get_email_from_json_credentials(json.loads(request.args['credentials']))
    except:
        return 'Wrong credentials.', 400
    return email
    
#Google OAuth2 related
@app.route('/access')
def access():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES)
    flow.redirect_uri = 'http://localhost:5000/oauth2callback'
    authorization_url, state = flow.authorization_url(
        approval_prompt='force',
        access_type='offline',
        include_granted_scopes='true')
    return jsonify({'url': authorization_url}), 200

@app.route('/oauth2callback')
def callback():
    state = request.args['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES,
        state=state)
    flow.redirect_uri = 'http://localhost:5000/oauth2callback'
    flow.fetch_token(code = request.args['code'])
    return flow.credentials.to_json(), 200

def get_email_from_json_credentials(json_creds):
    creds = Credentials.from_authorized_user_info(json_creds, SCOPES)
    service = build('oauth2', 'v2', credentials=creds)
    user_info = service.userinfo().get().execute()
    return user_info['email']

def handle_bad_request(e):
    return 'Bad request!', 400
app.register_error_handler(400, handle_bad_request)
app.run()
