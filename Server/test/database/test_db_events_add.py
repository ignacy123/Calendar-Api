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
    def test_add_event_non_existent_activity(self, _):
        self.assertRaises(db.NoSuchActivityException, db.add_event, test_email, datetime1, datetime3, weird_activity, None)
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_add_event_not_a_favourite_activity(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        self.assertRaises(psycopg2.errors.RaiseException, db.add_event, test_email, datetime1, datetime3, activity_name, None)
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_add_event_ends_before_starts(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        db.new_fav(test_email, activity_name)
        self.assertRaises(psycopg2.errors.CheckViolation, db.add_event, test_email, datetime3, datetime1, activity_name, None)
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_add_event_invalid_recurrence(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        self.assertRaises(psycopg2.errors.RaiseException, db.add_event, test_email, datetime1, datetime3, activity_name, weird_recurrence) 
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_add_event_single_overlap(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        db.new_fav(test_email, activity_name)
        db.add_event(test_email, datetime1, datetime3, activity_name, None)
        self.assertRaises(psycopg2.errors.RaiseException, db.add_event, test_email, datetime2, datetime4, activity_name, None) 
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_add_event_daily_longer_24hrs(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        db.new_fav(test_email, activity_name)
        #exactly 24 hours between datetime1 and datetime2
        self.assertRaises(psycopg2.errors.RaiseException, db.add_event, test_email, datetime1, datetime2, activity_name, 'DAILY')  
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_add_event_weekly_longer_7days(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        db.new_fav(test_email, activity_name)
        #exactly 7 days between datetime1 and datetime5
        self.assertRaises(psycopg2.errors.RaiseException, db.add_event, test_email, datetime1, datetime5, activity_name, 'WEEKLY') 
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_add_event_monthly_longer_28days(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        db.new_fav(test_email, activity_name)
        #exactly 28 days between datetime1 and datetime6
        self.assertRaises(psycopg2.errors.RaiseException, db.add_event, test_email, datetime1, datetime6, activity_name, 'MONTHLY') 
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_add_event_yearly_longer_365days(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        db.new_fav(test_email, activity_name)
        #exactly 365 days between datetime1 and datetime7
        self.assertRaises(psycopg2.errors.RaiseException, db.add_event, test_email, datetime1, datetime7, activity_name, 'YEARLY') 
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_add_event_monthly_starts_after_28(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        db.new_fav(test_email, activity_name)
        #day of datetime8 is strictly greater than 28
        self.assertRaises(psycopg2.errors.RaiseException, db.add_event, test_email, datetime8, datetime9, activity_name, 'MONTHLY') 
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_add_event_monthly_ends_after_28(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        db.new_fav(test_email, activity_name)
        #day of datetime8 is strictly greater than 28
        self.assertRaises(psycopg2.errors.RaiseException, db.add_event, test_email, datetime1, datetime8, activity_name, 'MONTHLY') 
        
    
