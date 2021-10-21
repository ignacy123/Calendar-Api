import pytest
from unittest.mock import patch
from src.server import app
import json

fake_token = {'token' : 'fake_token', 'refresh_token' : 'fake_refresh_token'}

def test_fav_get_no_token():
    response = app.test_client().get(
        '/fav',
        query_string = {}
        )
    data = response.json
    
    assert response.status_code == 401
    assert 'message' in data.keys()
    assert data['message'] == 'Please provide a Google Authentication token.'

@patch("src.googleservice.gs.token_to_creds_json_and_email", side_effect=Exception())
def test_fav_get_invalid_token(mock1):
    response = app.test_client().get(
        '/fav',
        query_string = {'token' : json.dumps(fake_token), 'name' : 'test'}
        )
    data = response.json
    
    mock1.assert_called_once_with(fake_token)
    assert response.status_code == 401
    assert 'message' in data.keys()
    assert data['message'] == 'Wrong credentials.'
    
@patch("src.googleservice.gs.token_to_creds_json_and_email", return_value=('creds', 'a@a.com'))
@patch("src.database.db.fav_activities", side_effect=Exception())
def test_fav_get_database_error(mock1, mock2):
    response = app.test_client().get(
        '/fav',
        query_string = {'token' : json.dumps(fake_token), 'name' : 'test'}
        )
    data = response.json
    
    mock2.assert_called_once_with(fake_token)
    mock1.assert_called_once_with('a@a.com')
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Database error.'
    
@patch("src.googleservice.gs.token_to_creds_json_and_email", return_value=('creds', 'a@a.com'))
@patch("src.database.db.fav_activities", return_value = [(1, 'swimming'), (2, 'bowling')])
def test_fav_get(mock1, mock2):
    response = app.test_client().get(
        '/fav',
        query_string = {'token' : json.dumps(fake_token), 'name' : 'test'}
        )
    data = response.json
    
    mock2.assert_called_once_with(fake_token)
    mock1.assert_called_once_with('a@a.com')
    assert response.status_code == 200
    assert 'activities' in data.keys()
    assert data['activities'] == [[1, 'swimming'], [2, 'bowling']]
