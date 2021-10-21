import pytest
import src.database.db as db
import json
from unittest.mock import patch
from src.server import app

fake_token = {'token' : 'fake_token', 'refresh_token' : 'fake_refresh_token'}

def test_event_get_no_token():
    response = app.test_client().get(
        '/event',
        query_string = {'date' : 'test'}
        )
    data = response.json
    
    assert response.status_code == 401
    assert 'message' in data.keys()
    assert data['message'] == 'Please provide a Google Authentication token.'

def test_event_get_no_date():
    response = app.test_client().get(
        '/event',
        query_string = {'token' : json.dumps(fake_token)}
        )
    data = response.json
    
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Please choose a date.'

@patch("src.googleservice.gs.token_to_creds_json_and_email", side_effect=Exception())
def test_event_get_invalid_token(mock1):
    response = app.test_client().get(
        '/event',
        query_string = {'token' : json.dumps(fake_token), 'date' : 'test'}
        )
    data = response.json
    
    mock1.assert_called_once_with(fake_token)
    assert response.status_code == 401
    assert 'message' in data.keys()
    assert data['message'] == 'Wrong credentials.'
   
@patch("src.googleservice.gs.token_to_creds_json_and_email", return_value=('creds', 'a@a.com'))
@patch("src.server.dateutil.parser.isoparse", side_effect=Exception())
def test_event_get_wrong_date(mock1, mock2):
    response = app.test_client().get(
        '/event',
        query_string = {'token' : json.dumps(fake_token), 'date' : 'test'}
        )
    data = response.json
    
    mock2.assert_called_once_with(fake_token)
    mock1.assert_called_once_with('test')
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Date not in an ISO format.'
   
@patch("src.googleservice.gs.token_to_creds_json_and_email", return_value=('creds', 'a@a.com'))
@patch("src.server.dateutil.parser.isoparse", return_value='date')
@patch("src.database.db.get_activities", side_effect=Exception())
def test_event_get_database_error(mock1, mock2, mock3):
    response = app.test_client().get(
        '/event',
        query_string = {'token' : json.dumps(fake_token), 'date' : 'test'}
        )
    data = response.json
    
    mock3.assert_called_once_with(fake_token)
    mock2.assert_called_once_with('test')
    mock1.assert_called_once_with('date', 'a@a.com')
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Database error.'
   
@patch("src.googleservice.gs.token_to_creds_json_and_email", return_value=('creds', 'a@a.com'))
@patch("src.server.dateutil.parser.isoparse", return_value='date')
@patch("src.database.db.get_activities", return_value=[['swimming', '2021-10-10T13:00:00', '2021-10-10T13:30:00', 'DAILY'], ['swimming', '2021-10-10T10:00:00', '2021-10-10T12:00:00', None]])
def test_event_get(mock1, mock2, mock3):
    response = app.test_client().get(
        '/event',
        query_string = {'token' : json.dumps(fake_token), 'date' : 'test'}
        )
    data = response.json
    
    mock3.assert_called_once_with(fake_token)
    mock2.assert_called_once_with('test')
    mock1.assert_called_once_with('date', 'a@a.com')
    assert response.status_code == 200
    assert 'activities' in data.keys()
    assert data['activities'] == [['swimming', '2021-10-10T13:00:00', '2021-10-10T13:30:00', 'DAILY'], ['swimming', '2021-10-10T10:00:00', '2021-10-10T12:00:00', None]]
    
    
