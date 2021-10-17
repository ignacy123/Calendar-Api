#!/bin/python3
import flask 
from flask import request, jsonify
import sys
import json
import datetime
import dateutil.parser
import database.db as db
import googleservice.gs as gs
import google.oauth2.credentials


app = flask.Flask(__name__)
app.config["DEBUG"] = True
try:
    db.start_db()
except:
    print("Could not start db. Aborting")
    sys.exit(-1)

@app.route('/lall', methods=['GET'])
def list_all():
    try:
        return jsonify(db.all_activities())
    except:
        message = 'Database error.'
        return jsonify({'message': message}), 400
        
@app.route('/fav', methods=['GET', 'PUT', 'DELETE'])
def fav():
    if 'credentials' not in request.args:
        message = 'Please provide a Google Authentication token.'
        return jsonify({'message': message}), 400
    if 'name' not in request.args and (flask.request.method == 'PUT' or flask.request.method == 'DELETE'):
        message = 'Please provide a name.'
        return jsonify({'message': message}), 400
        
    try:
        email = gs.get_email_from_json_credentials(json.loads(request.args['credentials']))
    except:
        message = 'Wrong credentials.'
        return jsonify({'message': message}), 400
    
    if request.method == 'GET':
        try:
            return jsonify(db.fav_activities(email))
        except:
            message = 'Database error.'
            return jsonify({'message': message}), 400
        
    if request.method == 'PUT':
        name = request.args['name']
        try:
            db.new_fav(email, name)
            return jsonify({'name' : name}), 200
        except db.NoSuchActivityException:
            message = 'Such activity does not exist.'
            return jsonify({'message': message}), 400
        except:
            message = 'Database error.'
            return jsonify({'message': message}), 400
            
    if request.method == 'DELETE':
        name = request.args['name']
        try:
            db.delete_fav(email, name)
            return jsonify({'name' : name}), 200
        except db.NoSuchActivityException as e:
            message = 'Such activity does not exist.'
            return jsonify({'message': message}), 400
        except:
            message = 'Database error.'
            return jsonify({'message': message}), 400
    
@app.route('/event', methods=['PUT', 'GET'])
def event():
    if 'credentials' not in request.args:
        message = 'Please provide a Google Authentication token.'
        return jsonify({'message': message}), 400
    if 'start_date' not in request.args and request.method == 'PUT':
        message = 'Please choose a start_date.'
        return jsonify({'message': message}), 400
    if 'end_date' not in request.args and request.method == 'PUT':
        message = 'Please choose an end_date.'
        return jsonify({'message': message}), 400
    if 'date' not in request.args and request.method == 'GET':
        message = 'Please choose a date.'
        return jsonify({'message': message}), 400
    if 'name' not in request.args and request.method == 'PUT':
        message = 'Please specify an activity.'
        return jsonify({'message': message}), 400
    
    json_creds = json.loads(request.args['credentials'])
    
    try:
        email = gs.get_email_from_json_credentials(json_creds)
    except:
        message = 'Wrong credentials.'
        return jsonify({'message': message}), 400
    
    if request.method == 'PUT':
        if 'recurrence' in request.args and request.args['recurrence'] not in ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY']:
            message = 'Unknown recurrence.'
            return jsonify({'message': message}), 400
        recurrence = None
        if 'recurrence' in request.args:
            recurrence = request.args['recurrence']
        try:
            start_date = dateutil.parser.isoparse(request.args['start_date'])
            end_date = dateutil.parser.isoparse(request.args['end_date'])
        except:
            message = 'Date not in an ISO format.'
            return jsonify({'message': message}), 400
            
        name = request.args['name']
        if start_date >= end_date:
            message = 'Event ends before it starts.'
            return jsonify({'message': message}), 400
        try:
            fav_activities = db.fav_activities(email)
        except:
            message = 'Database error.'
            return jsonify({'message': message}), 400
        if name not in [y for x, y in fav_activities]:
            message = 'Activity has to be a favourite.'
            return jsonify({'message': message}), 400
        try:
            db.add_event(email, start_date, end_date, name, recurrence)
        except:
            message = 'Database error.'
            return jsonify({'message': message}), 400
        try:
            gs.add_event_to_google_calendar(json_creds, start_date, end_date, name, recurrence)
        except:
            message = 'Saved to database but failed to upload to Google.'
            return jsonify({'message': message}), 400
        return jsonify({'name' : name, 'start_date' : start_date, 'end_date' : end_date, 'recurrence' : recurrence}), 200
    
    if request.method == 'GET':
        try:
            date = dateutil.parser.isoparse(request.args['date'])
        except:
            message = 'Date not in an ISO format.'
            return jsonify({'message': message}), 400
        try:
            res = {'activities' : db.get_activities(date, email)}
            return jsonify(res)
        except:
            message = 'Database error.'
            return jsonify({'message': message}), 400
        
    
@app.route('/email', methods=['GET'])
def email():
    if 'credentials' not in request.args:
        message = 'Please provide a Google Authentication token.'
        return jsonify({'message': message}), 400
    try:
        email = gs.get_email_from_json_credentials(json.loads(request.args['credentials']))
        return jsonify({'email' : email})
    except:
        message = 'Wrong credentials.'
        return jsonify({'message': message}), 400
    
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
    message = 'Bad request!'
    return jsonify({'message': message}), 400

def main():
    app.register_error_handler(400, handle_bad_request)
    app.run()

if __name__ == '__main__':
    main()
