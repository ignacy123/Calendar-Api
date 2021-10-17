#!/bin/python3
import flask 
from flask import request, jsonify
import json
import datetime
import dateutil.parser
import database.db as db
import googleservice.gs as gs
import google.oauth2.credentials


app = flask.Flask(__name__)
app.config["DEBUG"] = True
db.start_db()

@app.route('/lall', methods=['GET'])
def list_all():
    return jsonify(db.all_activities())

@app.route('/fav', methods=['GET', 'PUT', 'DELETE'])
def fav():
    if 'credentials' not in request.args:
        return "Please provide a Google Authentication token.", 400
    if 'name' not in request.args and (flask.request.method == 'PUT' or flask.request.method == 'DELETE'):
        return "Please provide a name.", 400
    
    try:
        email = gs.get_email_from_json_credentials(json.loads(request.args['credentials']))
    except:
        return 'Wrong credentials.', 400
    
    if request.method == 'GET':
        return jsonify(db.fav_activities(email))
    if request.method == 'PUT':
        name = request.args['name']
        db.new_fav(email, name)
        return jsonify([name]), 200
    if request.method == 'DELETE':
        name = request.args['name']
        db.delete_fav(email, name)
        return jsonify([name]), 200
    
@app.route('/event', methods=['PUT', 'GET'])
def event():
    if 'credentials' not in request.args:
        return "Please provide a Google Authentication token.", 400
    if 'start_date' not in request.args and request.method == 'PUT':
        return "Please choose a start_date.", 400
    if 'end_date' not in request.args and request.method == 'PUT':
        return "Please choose an end_date.", 400
    if 'date' not in request.args and request.method == 'GET':
        return "Please choose a date.", 400
    if 'name' not in request.args and request.method == 'PUT':
        return "Please specify an activity.", 400
    
    try:
        email = gs.get_email_from_json_credentials(json.loads(request.args['credentials']))
    except:
        return 'Wrong credentials.', 400
    
    if request.method == 'PUT':
        if 'recurrence' in request.args and request.args['recurrence'] not in ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY']:
            return "Unknown recurrence", 400
        recurrence = None
        if 'recurrence' in request.args:
            recurrence = request.args['recurrence']
        json_creds = json.loads(request.args['credentials'])
        start_date = dateutil.parser.isoparse(request.args['start_date'])
        end_date = dateutil.parser.isoparse(request.args['end_date'])
        name = request.args['name']
        if start_date >= end_date:
            return 'Events ends before it starts', 400
        if name not in [y for x, y in db.fav_activities(email)]:
            return 'Activity has to be a favourite', 400
        try:
            db.add_event(email, start_date, end_date, name, recurrence)
        except:
            return 'Database error.', 400
        try:
            gs.add_event_to_google_calendar(json_creds, start_date, end_date, name, recurrence)
        except:
            return 'Saved to database but failed to upload to Google.', 400
        return jsonify(request.args['name']), 200
    
    if request.method == 'GET':
        date = dateutil.parser.isoparse(request.args['date'])
        res = {'activities' : db.get_activities(date, email)}
        return jsonify(res)
        
    
@app.route('/email', methods=['GET'])
def email():
    if 'credentials' not in request.args:
        return "Please provide a Google Authentication token.", 400
    try:
        email = gs.get_email_from_json_credentials(json.loads(request.args['credentials']))
    except:
        return 'Wrong credentials.', 400
    return email
    
#Google OAuth2 related
@app.route('/access')
def access():
    authorization_url = gs.gen_auth_url()
    return jsonify({'url': authorization_url}), 200

@app.route('/oauth2callback')
def callback():
    creds_json = gs.code_to_creds_json(request.args['state'], request.args['code'])
    return creds_json, 200

def handle_bad_request(e):
    return 'Bad request!', 400

def main():
    app.register_error_handler(400, handle_bad_request)
    app.run()

if __name__ == '__main__':
    main()
