import pytest
from unittest.mock import patch
from src.server import app
import src.database.db as db
import json

fake_token = {'token' : 'fake_token', 'refresh_token' : 'fake_refresh_token'}
    
def test_fav_delete_no_token():
    response = app.test_client().delete(
        '/fav',
        query_string = {'name' : 'test'}
        )
    data = response.json
    
    assert response.status_code == 401
    assert 'message' in data.keys()
    assert data['message'] == 'Please provide a Google Authentication token.'
    
def test_fav_delete_no_name():
    response = app.test_client().delete(
        '/fav',
        query_string = {'token' : json.dumps(fake_token)}
        )
    data = response.json
    
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Please provide a name.'

@patch("src.googleservice.gs.token_to_creds_json_and_email", side_effect=Exception())
def test_fav_delete_invalid_token(mock1):
    response = app.test_client().delete(
        '/fav',
        query_string = {'token' : json.dumps(fake_token), 'name' : 'test'}
        )
    data = response.json
    
    mock1.assert_called_once_with(fake_token)
    assert response.status_code == 401
    assert 'message' in data.keys()
    assert data['message'] == 'Wrong credentials.'
    
@patch("src.googleservice.gs.token_to_creds_json_and_email", return_value=('creds', 'a@a.com'))
@patch("src.database.db.delete_fav", side_effect=db.NoSuchActivityException())
def test_fav_delete_wrong_name(mock1, mock2):
    response = app.test_client().delete(
        '/fav',
        query_string = {'token' : json.dumps(fake_token), 'name' : 'test'}
        )
    data = response.json
    
    mock2.assert_called_once_with(fake_token)
    mock1.assert_called_once_with('a@a.com', 'test')
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Such activity does not exist.'
    
@patch("src.googleservice.gs.token_to_creds_json_and_email", return_value=('creds', 'a@a.com'))
@patch("src.database.db.delete_fav", side_effect=Exception())
def test_fav_delete_database_error(mock1, mock2):
    response = app.test_client().delete(
        '/fav',
        query_string = {'token' : json.dumps(fake_token), 'name' : 'test'}
        )
    data = response.json
    
    mock2.assert_called_once_with(fake_token)
    mock1.assert_called_once_with('a@a.com', 'test')
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Database error.'
    
@patch("src.googleservice.gs.token_to_creds_json_and_email", return_value=('creds', 'a@a.com'))
@patch("src.database.db.delete_fav", return_value=None)
def test_fav(mock1, mock2):
    response = app.test_client().delete(
        '/fav',
        query_string = {'token' : json.dumps(fake_token), 'name' : 'test'}
        )
    data = response.json
    
    mock2.assert_called_once_with(fake_token)
    mock1.assert_called_once_with('a@a.com', 'test')
    assert response.status_code == 200
    assert 'name' in data.keys()
    assert data['name'] == 'test' 
