#!/bin/python3

import flask 
from flask import request, jsonify
import json
import datetime
import argparse
import database
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

fav_activites = []
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/userinfo.email', 'openid']
DB_HOST = "localhost"
DB_PORT = 5432

#Database can be on any server now
parser = argparse.ArgumentParser()
parser.add_argument('--dbhost', default=DB_HOST)
parser.add_argument('--dbport', default=DB_PORT)
args = parser.parse_args()

database.set_host(args.dbhost)
database.set_port(args.dbport)

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
    
    if flask.request.method == 'GET':
        return jsonify(database.fav_activities(email))
    if flask.request.method == 'PUT':
        name = request.args['name']
        database.new_fav(email, name)
        return jsonify([name]), 200
    if flask.request.method == 'DELETE':
        name = request.args['name']
        database.remove_fav(email, name)
        return jsonify([name]), 200
    
    
@app.route('/email', methods=['GET'])
def email():
    if 'credentials' not in request.args:
        return "Please provide a Google Authentication token.", 400
    return get_email_from_json_credentials(json.loads(request.args['credentials']))
    
#Google OAuth2 related
@app.route('/access')
def access():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES)
    flow.redirect_uri = 'http://localhost:5000/oauth2callback'
    authorization_url, state = flow.authorization_url(
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
    return jsonify_credentials(flow.credentials), 200

def get_email_from_json_credentials(json_creds):
    creds = Credentials.from_authorized_user_info(json_creds, SCOPES)
    service = build('oauth2', 'v2', credentials=creds)
    user_info = service.userinfo().get().execute()
    return user_info['email']

def jsonify_credentials(credentials):
    credentials_dict = {
    'token': credentials.token,
    'refresh_token': credentials.refresh_token,
    'token_uri': credentials.token_uri,
    'client_id': credentials.client_id,
    'client_secret': credentials.client_secret,
    'scopes': credentials.scopes}
    return jsonify(credentials_dict)


def handle_bad_request(e):
    return 'Bad request!', 400
app.register_error_handler(400, handle_bad_request)
app.run()
