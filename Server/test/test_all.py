import pytest
from unittest.mock import patch
from src.server import app
import json

def test_list_all():
    response = app.test_client().get('/all')
    
    assert response.status_code == 200
    assert 'activities' in response.json.keys() 

@patch("src.database.db.all_activities", side_effect=Exception())
def test_list_all_db_fail(mock1):
    response = app.test_client().get('/all')
    data = response.json
        
    assert response.status_code == 400
    assert 'message' in data.keys()
    assert data['message'] == 'Database error.'
