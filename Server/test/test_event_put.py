import pytest
import src.database.db as db
import json
from datetime import datetime
from unittest.mock import patch
from unittest.mock import call
from src.server import app

fake_token = {'token' : 'fake_token', 'refresh_token' : 'fake_refresh_token'}

def test_event_put_no_token():
    response = app.test_client().put(
        '/event',
        query_string = {'start_date' : 'test', 'end_date' : 'test', 'name' : 'test'}
        )
    data = response.json
    
    assert response.status_code == 401
    assert 'message' in data.keys()
    assert data['message'] == 'Please provide a Google Authentication token.'

def test_event_put_no_start_date():
    response = app.test_client().put(
        '/event',
        query_string = {'token' : json.dumps(fake_token), 'end_date' : 'test', 'name' : 'test'}
        )
    data = response.json
    
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Please choose a start_date.'

def test_event_put_no_end_date():
    response = app.test_client().put(
        '/event',
        query_string = {'token' : json.dumps(fake_token), 'start_date' : 'test', 'name' : 'test'}
        )
    data = response.json
    
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Please choose an end_date.'

def test_event_put_no_activity():
    response = app.test_client().put(
        '/event',
        query_string = {'token' : json.dumps(fake_token), 'start_date' : 'test', 'end_date' : 'test'}
        )
    data = response.json
    
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Please specify an activity.'

def test_event_put_wrong_recurrence():
    response = app.test_client().put(
        '/event',
        query_string = {'token' : json.dumps(fake_token), 'start_date' : 'test', 'end_date' : 'test', 'name' : 'test', 'recurrence' : 'WEIRD_RECURRENCE'}
        )
    data = response.json
    
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Unknown recurrence.'

@patch("src.googleservice.gs.token_to_creds_json_and_email", side_effect=Exception())
def test_event_put_invalid_token(mock1):
    response = app.test_client().put(
        '/event',
        query_string = {'token' : json.dumps(fake_token), 'start_date' : 'test', 'end_date' : 'test', 'name' : 'test'}
        )
    data = response.json
    
    mock1.assert_called_once_with(fake_token)
    assert response.status_code == 401
    assert 'message' in data.keys()
    assert data['message'] == 'Wrong credentials.'

@patch("src.googleservice.gs.token_to_creds_json_and_email", return_value=('creds', 'a@a.com'))
@patch("src.server.dateutil.parser.isoparse", side_effect=Exception())
def test_event_put_invalid_date(mock1, mock2):
    response = app.test_client().put(
        '/event',
        query_string = {'token' : json.dumps(fake_token), 'start_date' : 'start_test', 'end_date' : 'end_test', 'name' : 'test'}
        )
    data = response.json
    
    mock2.assert_called_once_with(fake_token)
    mock1.assert_called_once_with('start_test')
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Date not in an ISO format.'

def fake_parser_start_after_end(x):
    if x=='start_test':
        return datetime(year=2021, month=10, day=21, hour=10, minute=10)
    elif x=='end_test':
        return datetime(year=2021, month=10, day=20, hour=10, minute=10)
    else:
        return None
    
@patch("src.googleservice.gs.token_to_creds_json_and_email", return_value=('creds', 'a@a.com'))
@patch("src.server.dateutil.parser.isoparse", side_effect=fake_parser_start_after_end)
def test_event_put_start_after_end(mock1, mock2):
    response = app.test_client().put(
        '/event',
        query_string = {'token' : json.dumps(fake_token), 'start_date' : 'start_test', 'end_date' : 'end_test', 'name' : 'test'}
        )
    data = response.json
    
    mock2.assert_called_once_with(fake_token)
    mock1.assert_has_calls([call('start_test'), call('end_test')])
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Event ends before it starts.'

def fake_parser_start_before_end(x):
    if x=='start_test':
        return datetime(year=2021, month=10, day=20, hour=10, minute=10)
    elif x=='end_test':
        return datetime(year=2021, month=10, day=21, hour=10, minute=10)
    else:
        return None
    
@patch("src.googleservice.gs.token_to_creds_json_and_email", return_value=('creds', 'a@a.com'))
@patch("src.server.dateutil.parser.isoparse", side_effect=fake_parser_start_before_end)
@patch("src.database.db.fav_activities", side_effect=Exception())
def test_event_put_fav_activity_database_error(mock1, mock2, mock3):
    response = app.test_client().put(
        '/event',
        query_string = {'token' : json.dumps(fake_token), 'start_date' : 'start_test', 'end_date' : 'end_test', 'name' : 'test'}
        )
    data = response.json
    
    mock3.assert_called_once_with(fake_token)
    mock2.assert_has_calls([call('start_test'), call('end_test')])
    mock1.assert_called_once_with('a@a.com')
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Database error when extracting favourite activities.'
    
@patch("src.googleservice.gs.token_to_creds_json_and_email", return_value=('creds', 'a@a.com'))
@patch("src.server.dateutil.parser.isoparse", side_effect=fake_parser_start_before_end)
@patch("src.database.db.fav_activities", return_value=[(1, 'not test'), (2, 'also not test'), (3, 'still no test')])
def test_event_put_activity_not_a_favourite(mock1, mock2, mock3):
    response = app.test_client().put(
        '/event',
        query_string = {'token' : json.dumps(fake_token), 'start_date' : 'start_test', 'end_date' : 'end_test', 'name' : 'test'}
        )
    data = response.json
    
    mock3.assert_called_once_with(fake_token)
    mock2.assert_has_calls([call('start_test'), call('end_test')])
    mock1.assert_called_once_with('a@a.com')
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Activity has to be a favourite.'
    
@patch("src.googleservice.gs.token_to_creds_json_and_email", return_value=('creds', 'a@a.com'))
@patch("src.server.dateutil.parser.isoparse", side_effect=fake_parser_start_before_end)
@patch("src.database.db.fav_activities", return_value=[(1, 'not test'), (2, 'also not test'), (3, 'still no test'), (4, 'test')])
@patch("src.database.db.add_event", side_effect=Exception())
def test_event_put_actual_database_error(mock1, mock2, mock3, mock4):
    response = app.test_client().put(
        '/event',
        query_string = {'token' : json.dumps(fake_token), 'start_date' : 'start_test', 'end_date' : 'end_test', 'name' : 'test', 'recurrence' : 'DAILY'}
        )
    data = response.json
    
    mock4.assert_called_once_with(fake_token)
    mock3.assert_has_calls([call('start_test'), call('end_test')])
    mock2.assert_called_once_with('a@a.com')
    mock1.assert_called_once_with('a@a.com', datetime(year=2021, month=10, day=20, hour=10, minute=10), datetime(year=2021, month=10, day=21, hour=10, minute=10), 'test', 'DAILY')
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Database error.'
    
@patch("src.googleservice.gs.token_to_creds_json_and_email", return_value=('creds', 'a@a.com'))
@patch("src.server.dateutil.parser.isoparse", side_effect=fake_parser_start_before_end)
@patch("src.database.db.fav_activities", return_value=[(1, 'not test'), (2, 'also not test'), (3, 'still no test'), (4, 'test')])
@patch("src.database.db.add_event", return_value=None)
@patch("src.googleservice.gs.add_event_to_google_calendar", side_effect=Exception())
def test_event_put_googleservice_error(mock1, mock2, mock3, mock4, mock5):
    response = app.test_client().put(
        '/event',
        query_string = {'token' : json.dumps(fake_token), 'start_date' : 'start_test', 'end_date' : 'end_test', 'name' : 'test', 'recurrence' : 'DAILY'}
        )
    data = response.json
    
    mock5.assert_called_once_with(fake_token)
    mock4.assert_has_calls([call('start_test'), call('end_test')])
    mock3.assert_called_once_with('a@a.com')
    mock2.assert_called_once_with('a@a.com', datetime(year=2021, month=10, day=20, hour=10, minute=10), datetime(year=2021, month=10, day=21, hour=10, minute=10), 'test', 'DAILY')
    mock1.assert_called_once_with('creds', datetime(year=2021, month=10, day=20, hour=10, minute=10), datetime(year=2021, month=10, day=21, hour=10, minute=10), 'test', 'DAILY')
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Saved to database but failed to upload to Google.'
    
@patch("src.googleservice.gs.token_to_creds_json_and_email", return_value=('creds', 'a@a.com'))
@patch("src.server.dateutil.parser.isoparse", side_effect=fake_parser_start_before_end)
@patch("src.database.db.fav_activities", return_value=[(1, 'not test'), (2, 'also not test'), (3, 'still no test'), (4, 'test')])
@patch("src.database.db.add_event", return_value=None)
@patch("src.googleservice.gs.add_event_to_google_calendar", return_value=None)
def test_event_put(mock1, mock2, mock3, mock4, mock5):
    response = app.test_client().put(
        '/event',
        query_string = {'token' : json.dumps(fake_token), 'start_date' : 'start_test', 'end_date' : 'end_test', 'name' : 'test', 'recurrence' : 'DAILY'}
        )
    data = response.json
    
    mock5.assert_called_once_with(fake_token)
    mock4.assert_has_calls([call('start_test'), call('end_test')])
    mock3.assert_called_once_with('a@a.com')
    mock2.assert_called_once_with('a@a.com', datetime(year=2021, month=10, day=20, hour=10, minute=10), datetime(year=2021, month=10, day=21, hour=10, minute=10), 'test', 'DAILY')
    mock1.assert_called_once_with('creds', datetime(year=2021, month=10, day=20, hour=10, minute=10), datetime(year=2021, month=10, day=21, hour=10, minute=10), 'test', 'DAILY')
    assert response.status_code == 200
    assert 'name' in data.keys()
    assert data['name'] == 'test'
    assert 'start_date' in data.keys()
    assert data['start_date'] == 'start_test'
    assert 'end_date' in data.keys()
    assert data['end_date'] == 'end_test'
    assert 'recurrence' in data.keys()
    assert data['recurrence'] == 'DAILY'
    
    






