import src.database.db as db
import psycopg2
from unittest.mock import patch
from unittest import TestCase
from .common import *
from datetime import timedelta

class MockDB(TestCase):
    @patch('src.database.db.config', side_effect=fake_config)
    def setUp(self, _):
        db.start_db()
    @patch('src.database.db.config', side_effect=fake_config)
    def tearDown(self, _):
        db.drop_db()
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_one_single_activity(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        db.new_fav(test_email, activity_name)
        db.add_event(test_email, datetime1, datetime3, activity_name, None)
        date = datetime1.replace(hour = 0, minute = 0)
        activities = db.get_activities(date, test_email)
        
        assert len(activities) == 1
        assert (activity_name, datetime1.isoformat(), datetime3.isoformat(), None) in activities
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_daily_simple(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        db.new_fav(test_email, activity_name)
        db.add_event(test_email, datetime1, datetime10, activity_name, 'DAILY')
        date = datetime1.replace(hour = 0, minute = 0)
        activities_day_before = db.get_activities(date - timedelta(days = 1), test_email)
        activities_same_day = db.get_activities(date, test_email)
        activities_day_after = db.get_activities(date + timedelta(days = 1), test_email)
        activities_long_after = db.get_activities(date + timedelta(days = 10000), test_email)
        
        assert len(activities_day_before) == 0
        
        assert len(activities_same_day) == 1
        assert (activity_name, datetime1.isoformat(), datetime10.isoformat(), 'DAILY') in activities_same_day
        
        assert len(activities_day_after) == 1
        assert (activity_name, datetime1.isoformat(), datetime10.isoformat(), 'DAILY') in activities_day_after
        
        assert len(activities_long_after) == 1
        assert (activity_name, datetime1.isoformat(), datetime10.isoformat(), 'DAILY') in activities_long_after
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_weekly_simple(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        db.new_fav(test_email, activity_name)
        db.add_event(test_email, datetime1, datetime10, activity_name, 'WEEKLY')
        date = datetime1.replace(hour = 0, minute = 0)
        activities_week_before = db.get_activities(date - timedelta(days = 7), test_email)
        activities_same_day = db.get_activities(date, test_email)
        activities_week_after = db.get_activities(date + timedelta(days = 7), test_email)
        activities_wrong_dow = db.get_activities(date + timedelta(days = 11), test_email)
        activities_long_after = db.get_activities(date + timedelta(days = 7*10000), test_email)
        activities_long_after_wrong_dow = db.get_activities(date + timedelta(days = 7*10000+6), test_email)
        
        assert len(activities_week_before) == 0
        
        assert len(activities_wrong_dow) == 0
        
        assert len(activities_same_day) == 1
        assert (activity_name, datetime1.isoformat(), datetime10.isoformat(), 'WEEKLY') in activities_same_day
        
        assert len(activities_week_after) == 1
        assert (activity_name, datetime1.isoformat(), datetime10.isoformat(), 'WEEKLY') in activities_week_after
        
        assert len(activities_long_after) == 1
        assert (activity_name, datetime1.isoformat(), datetime10.isoformat(), 'WEEKLY') in activities_long_after
        
        assert len(activities_long_after_wrong_dow) == 0
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_weekly_long_event(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        db.new_fav(test_email, activity_name)
        #Tuesday to Friday
        db.add_event(test_email, datetime1, datetime4, activity_name, 'WEEKLY')
        date = datetime1.replace(hour = 0, minute = 0)
        activities_week_before_correct = db.get_activities(date - timedelta(days = 5), test_email)
        activities_same_week_correct = db.get_activities(date + timedelta(days = 2), test_email)
        activities_same_week_wrong = db.get_activities(date + timedelta(days = 6), test_email)
        activities_long_after_correct = db.get_activities(date + timedelta(days = 7*1000 + 2), test_email)
        activities_long_after_wrong = db.get_activities(date + timedelta(days = 7*1000 + 4), test_email)
        
        assert len(activities_week_before_correct) == 0
        
        assert len(activities_same_week_wrong) == 0
        
        assert len(activities_long_after_wrong) == 0
        
        assert len(activities_same_week_correct) == 1
        assert (activity_name, datetime1.isoformat(), datetime4.isoformat(), 'WEEKLY') in activities_same_week_correct
        
        assert len(activities_long_after_correct) == 1
        assert (activity_name, datetime1.isoformat(), datetime4.isoformat(), 'WEEKLY') in activities_long_after_correct
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_monthly_simple(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        db.new_fav(test_email, activity_name)
        db.add_event(test_email, datetime1, datetime10, activity_name, 'MONTHLY')
        date = datetime1.replace(hour = 0, minute = 0)
        activities_month_before = db.get_activities(date_minus_one_month(date), test_email)
        activities_same_day = db.get_activities(date, test_email)
        activities_month_after = db.get_activities(date_plus_one_month(date), test_email)
        activities_wrong_day = db.get_activities(date + timedelta(days = 11), test_email)
        activities_long_after = db.get_activities(date_plus_x_months(date, 1000), test_email)
        activities_long_after_wrong_day = db.get_activities(date_plus_x_months(date, 1000) + timedelta(days = 11), test_email)
        
        assert len(activities_month_before) == 0
        
        assert len(activities_wrong_day) == 0
        
        assert len(activities_same_day) == 1
        assert (activity_name, datetime1.isoformat(), datetime10.isoformat(), 'MONTHLY') in activities_same_day
        
        assert len(activities_month_after) == 1
        assert (activity_name, datetime1.isoformat(), datetime10.isoformat(), 'MONTHLY') in activities_month_after
        
        assert len(activities_long_after) == 1
        assert (activity_name, datetime1.isoformat(), datetime10.isoformat(), 'MONTHLY') in activities_long_after
        
        assert len(activities_long_after_wrong_day) == 0
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_monthly_long_event(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        db.new_fav(test_email, activity_name)
        #from 10.19 to 11.03
        db.add_event(test_email, datetime1, datetime11, activity_name, 'MONTHLY')
        date = datetime1.replace(hour = 0, minute = 0)
        activities_month_before_correct = db.get_activities(date_minus_one_month(date) + timedelta(days = 5), test_email)
        activities_same_month_correct = db.get_activities(date + timedelta(days = 13), test_email)
        activities_same_month_wrong = db.get_activities(date + timedelta(days = 29), test_email)
        activities_long_after_correct = db.get_activities(date_plus_x_months(date, 1000) + timedelta(days = 6), test_email)
        activities_long_after_wrong_day = db.get_activities(date_plus_x_months(date, 4000) - timedelta(days = 2), test_email)
        
        assert len(activities_month_before_correct) == 0
        
        assert len(activities_same_month_wrong) == 0
        
        assert len(activities_long_after_wrong_day) == 0
        
        assert len(activities_same_month_correct) == 1
        assert (activity_name, datetime1.isoformat(), datetime11.isoformat(), 'MONTHLY') in activities_same_month_correct
        
        assert len(activities_long_after_correct) == 1
        assert (activity_name, datetime1.isoformat(), datetime11.isoformat(), 'MONTHLY') in activities_long_after_correct
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_yearly_simple(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        db.new_fav(test_email, activity_name)
        db.add_event(test_email, datetime1, datetime10, activity_name, 'YEARLY')
        date = datetime1.replace(hour = 0, minute = 0)
        activities_year_before = db.get_activities(date_minus_x_years(date, 1), test_email)
        activities_same_day = db.get_activities(date, test_email)
        activities_year_after = db.get_activities(date_plus_x_years(date, 1), test_email)
        activities_wrong_day = db.get_activities(date + timedelta(days = 111), test_email)
        activities_long_after = db.get_activities(date_plus_x_years(date, 1000), test_email)
        activities_long_after_wrong_day = db.get_activities(date_plus_x_years(date, 2000) + timedelta(days = 200), test_email)
        
        assert len(activities_year_before) == 0
        
        assert len(activities_wrong_day) == 0
        
        assert len(activities_same_day) == 1
        assert (activity_name, datetime1.isoformat(), datetime10.isoformat(), 'YEARLY') in activities_same_day
        
        assert len(activities_year_after) == 1
        assert (activity_name, datetime1.isoformat(), datetime10.isoformat(), 'YEARLY') in activities_year_after
        
        assert len(activities_long_after) == 1
        assert (activity_name, datetime1.isoformat(), datetime10.isoformat(), 'YEARLY') in activities_long_after
        
        assert len(activities_long_after_wrong_day) == 0
        
    @patch('src.database.db.config', side_effect=fake_config)
    def test_yearly_long_event(self, _):
        activities = db.all_activities()
        activity_name = activities[0][1]
        db.new_fav(test_email, activity_name)
        #from 10.19 to 04.30
        db.add_event(test_email, datetime1, datetime12, activity_name, 'YEARLY')
        date = datetime1.replace(hour = 0, minute = 0)
        activities_year_before_correct = db.get_activities(date_minus_x_years(date, 1) + timedelta(days = 50), test_email)
        activities_same_year_correct = db.get_activities(date + timedelta(days = 130), test_email)
        activities_same_year_wrong = db.get_activities(date + timedelta(days = 290), test_email)
        activities_long_after_correct = db.get_activities(date_plus_x_years(date, 1000) + timedelta(days = 60), test_email)
        activities_long_after_wrong_day = db.get_activities(date_plus_x_years(date, 4000) - timedelta(days = 20), test_email)
        
        assert len(activities_year_before_correct) == 0
        
        assert len(activities_same_year_wrong) == 0
        
        assert len(activities_long_after_wrong_day) == 0
        
        assert len(activities_same_year_correct) == 1
        assert (activity_name, datetime1.isoformat(), datetime12.isoformat(), 'YEARLY') in activities_same_year_correct
        
        assert len(activities_long_after_correct) == 1
        assert (activity_name, datetime1.isoformat(), datetime12.isoformat(), 'YEARLY') in activities_long_after_correct
