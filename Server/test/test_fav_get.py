import pytest
from unittest.mock import patch
from src.server import app
import json
    
def test_fav_get_no_token():
    response = app.test_client().get('/fav')
    data = response.json
    
    assert response.status_code == 401
    assert 'message' in data.keys()
    assert data['message'] == 'Please provide a Google Authentication token.'
    
def test_fav_get_invalid_token():
    response = app.test_client().get(
        '/fav',
        query_string = {'token' : '{}', 'name' : 'test'}
        )
    data = response.json
    
    assert response.status_code == 401
    assert 'message' in data.keys()
    assert data['message'] == 'Wrong credentials.'
    
@patch("src.googleservice.gs.get_email_from_token_dict", return_value='a@a.com')
@patch("src.database.db.fav_activities", side_effect=Exception())
def test_fav_get_database_error(mock1, mock2):
    response = app.test_client().get(
        '/fav',
        query_string = {'token' : '{}', 'name' : 'test'}
        )
    data = response.json
    
    mock1.assert_called_once_with('a@a.com')
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Database error.'
    
@patch("src.googleservice.gs.get_email_from_token_dict", return_value='a@a.com')
@patch("src.database.db.fav_activities", return_value = [(1, 'swimming'), (2, 'bowling')])
def test_fav_get(mock1, mock2):
    response = app.test_client().get(
        '/fav',
        query_string = {'token' : '{}', 'name' : 'test'}
        )
    data = response.json
    
    mock1.assert_called_once_with('a@a.com')
    assert response.status_code == 200
    assert 'activities' in data.keys()
    assert data['activities'] == [[1, 'swimming'], [2, 'bowling']]
    
    
def test_fav_put_no_name():
    response = app.test_client().put(
        '/fav',
        query_string = {'token' : '{}'}
        )
    data = response.json
    
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Please provide a name.'
    
def test_fav_delete_no_token():
    response = app.test_client().delete(
        '/fav',
        query_string = {'name' : 'test'}
        )
    data = response.json
    
    assert response.status_code == 401
    assert 'message' in data.keys()
    assert data['message'] == 'Please provide a Google Authentication token.' 
