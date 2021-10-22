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
    def test_add_fav(self, _):
        empty_fav = db.fav_activities(test_email)
        
        assert len(empty_fav) == 0
        
        activities = db.all_activities()
        db.new_fav(test_email, activities[0][1])
        db.new_fav(test_email, activities[1][1])
        fav_activities_names = [y for x,y in db.fav_activities(test_email)]
        
        assert activities[0][1] in fav_activities_names
        assert activities[1][1] in fav_activities_names
        assert len(fav_activities_names) == 2
    
    @patch('src.database.db.config', side_effect=fake_config)
    def test_add_fav_non_existent(self, _):
        self.assertRaises(db.NoSuchActivityException, db.new_fav, test_email, weird_activity)
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_delete_fav(self, _):
        empty_fav = db.fav_activities(test_email)
        activities = db.all_activities()
        db.new_fav(test_email, activities[0][1])
        db.delete_fav(test_email, activities[0][1])
        fav_activities_names = [y for x,y in db.fav_activities(test_email)]
        
        assert activities[0][1] not in fav_activities_names
        assert len(fav_activities_names) == 0
    
    @patch('src.database.db.config', side_effect=fake_config)
    def test_delete_fav_non_existent(self, _):
        self.assertRaises(db.NoSuchActivityException, db.delete_fav, test_email, weird_activity)
