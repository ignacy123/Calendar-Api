#!/bin/python3
import flask 
from flask import Flask
from flask import request, jsonify
import sys
import json
import dateutil.parser
import src.database.db as db
import src.googleservice.gs as gs

app = Flask(__name__)
app.config["DEBUG"] = True

try:
    db.start_db()
except:
    print("Could not start db. Aborting")
    sys.exit(-1)

def handle_bad_request(e):
    message = 'Bad request!'
    return jsonify({'message': message}), 400
app.register_error_handler(400, handle_bad_request)

@app.route('/all', methods=['GET'])
def list_all():
    try:
        all_act = db.all_activities()
        return jsonify({'activities' : all_act})
    except:
        message = 'Database error.'
        return jsonify({'message': message}), 400
        
@app.route('/fav', methods=['GET', 'PUT', 'DELETE'])
def fav():
    if 'token' not in request.args:
        message = 'Please provide a Google Authentication token.'
        return jsonify({'message': message}), 401
    if 'name' not in request.args and (flask.request.method == 'PUT' or flask.request.method == 'DELETE'):
        message = 'Please provide a name.'
        return jsonify({'message': message}), 400
    
    try:
        creds_json, email = gs.token_to_creds_json_and_email(json.loads(request.args['token']))
    except:
        message = 'Wrong credentials.'
        return jsonify({'message': message}), 401
    
    if request.method == 'GET':
        try:
            fav_act = db.fav_activities(email)
            return jsonify({'activities' : fav_act})
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
    if 'token' not in request.args:
        message = 'Please provide a Google Authentication token.'
        return jsonify({'message': message}), 401
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
    if 'recurrence' in request.args and request.args['recurrence'] not in ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY'] and request.method == 'PUT':
        message = 'Unknown recurrence.'
        return jsonify({'message': message}), 400
    
    try:
        creds_json, email = gs.token_to_creds_json_and_email(json.loads(request.args['token']))
    except:
        message = 'Wrong credentials.'
        return jsonify({'message': message}), 401
    
    if request.method == 'PUT':
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
            message = 'Database error when extracting favourite activities.'
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
            gs.add_event_to_google_calendar(creds_json, start_date, end_date, name, recurrence)
        except:
            message = 'Saved to database but failed to upload to Google.'
            return jsonify({'message': message}), 400
        org_start_date = request.args['start_date']
        org_end_date = request.args['end_date']
        return jsonify({'name' : name, 'start_date' : org_start_date, 'end_date' : org_end_date, 'recurrence' : recurrence}), 200
    
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
    if 'token' not in request.args:
        message = 'Please provide a Google Authentication token.'
        return jsonify({'message': message}), 401
    try:
        creds_json, email = gs.token_to_creds_json_and_email(json.loads(request.args['token']))
        return jsonify({'email' : email})
    except:
        message = 'Wrong credentials.'
        return jsonify({'message': message}), 401
    
#Google OAuth2 related
@app.route('/access')
def access():
    authorization_url = gs.gen_auth_url()
    return jsonify({'url': authorization_url}), 200

@app.route('/oauth2callback')
def callback():
    creds_json = gs.code_to_creds_json(request.args['state'], request.args['code'])
    token_json = {'token' : creds_json['token'], 'refresh_token' : creds_json['refresh_token']}
    return token_json, 200

if __name__ == '__main__':
    app.run()

