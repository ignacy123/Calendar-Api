import pytest
import src.database.db as db
import json
from unittest.mock import patch
from src.server import app 

fake_token = {'token' : 'fake_token', 'refresh_token' : 'fake_refresh_token'}

def test_email_no_token():
    response = app.test_client().get(
        '/email',
        query_string = {}
        )
    data = response.json
    
    assert response.status_code == 401
    assert 'message' in data.keys()
    assert data['message'] == 'Please provide a Google Authentication token.'

@patch("src.googleservice.gs.token_to_creds_json_and_email", side_effect=Exception())
def test_email_invalid_token(mock1):
    response = app.test_client().get(
        '/email',
        query_string = {'token' : json.dumps(fake_token)}
        )
    data = response.json
    
    mock1.assert_called_once_with(fake_token)
    assert response.status_code == 401
    assert 'message' in data.keys()
    assert data['message'] == 'Wrong credentials.'

@patch("src.googleservice.gs.token_to_creds_json_and_email", return_value=('creds', 'a@a.com'))
def test_email(mock1):
    response = app.test_client().get(
        '/email',
        query_string = {'token' : json.dumps(fake_token)}
        )
    data = response.json
    
    mock1.assert_called_once_with(fake_token)
    assert response.status_code == 200
    assert 'email' in data.keys()
    assert data['email'] == 'a@a.com'
