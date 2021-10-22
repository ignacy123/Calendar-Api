import src.database.db as db
import psycopg2
from unittest.mock import patch
from unittest import TestCase
from .common import *

class MockDB(TestCase):
    @patch('src.database.db.config', side_effect=fake_config)
    def setUp(self, _):
        db.start_db()
    @patch('src.database.db.config', side_effect=fake_config)
    def tearDown(self, _):
        db.drop_db()
    
    @patch('src.database.db.config', side_effect=fake_config)
    def test_all_activities(self, _):
        activities = db.all_activities()
        
        assert len(activities) > 2
        assert len(activities[0]) == 2
        
    
