import pytest
from unittest.mock import patch
from src.server import app
import json

@patch("src.database.db.all_activities", side_effect=Exception())
def test_list_all_db_fail(mock1):
    response = app.test_client().get('/all')
    data = response.json
        
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Database error.'

@patch("src.database.db.all_activities", return_value=[(1, 'swimming'), (2, 'gokarts')])
def test_list_all(mock1):
    response = app.test_client().get('/all')
    
    assert response.status_code == 200
    assert 'activities' in response.json.keys() 
    assert response.json['activities'] == [[1, 'swimming'], [2, 'gokarts']]
