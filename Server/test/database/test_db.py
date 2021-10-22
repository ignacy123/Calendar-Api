import src.database.db as db
import pkgutil
from unittest.mock import patch
from unittest import TestCase
from configparser import ConfigParser
        
test_email = 'a@a.com'
    
def fake_config(filename='test_database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    config_data = pkgutil.get_data(__package__, filename).decode()
    parser.read_string(config_data)
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db

class MockDB(TestCase):
    @patch('src.database.db.config', side_effect=fake_config)
    def setUp(self, _):
        db.start_db()
    @patch('src.database.db.config', side_effect=fake_config)
    def tearDown(self, _):
        db.drop_db()
        
    def test_all_activities(self):
        activities = db.all_activities()
        
        assert len(activities) > 2
        assert len(activities[0]) == 2
    
    def test_add_fav(self):
        empty_fav = db.fav_activities(test_email)
        
        assert len(empty_fav) == 0
        
        activities = db.all_activities()
        db.new_fav(test_email, activities[0][1])
        db.new_fav(test_email, activities[1][1])
        fav_activities_names = [y for x,y in db.fav_activities(test_email)]
        
        assert activities[0][1] in fav_activities_names
        assert activities[1][1] in fav_activities_names
        assert len(fav_activities_names) == 2
        
    def test_add_fav_non_existent(self):
        self.assertRaises(db.NoSuchActivityException, db.new_fav, test_email, 'weird activity that for sure is not in the db')
        
    def test_delete_fav(self):
        empty_fav = db.fav_activities(test_email)
        activities = db.all_activities()
        db.new_fav(test_email, activities[0][1])
        db.delete_fav(test_email, activities[0][1])
        fav_activities_names = [y for x,y in db.fav_activities(test_email)]
        
        assert activities[0][1] not in fav_activities_names
    
    def test_delete_fav_non_existent(self):
        self.assertRaises(db.NoSuchActivityException, db.delete_fav, test_email, 'weird activity that for sure is not in the db')
        
        
