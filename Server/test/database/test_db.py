import src.database.db as db
import pkgutil
from unittest.mock import patch
from unittest import TestCase
from configparser import ConfigParser
    
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

#@patch('src.database.db.config', side_effect=fake_config)
#def test_simple(mock1):
    #db.start_db()
    #assert True


class MockDB(TestCase):
    @patch('src.database.db.config', side_effect=fake_config)
    def setUp(self, mock1):
        db.start_db()
    @patch('src.database.db.config', side_effect=fake_config)
    def tearDown(self, mock2):
        db.drop_db()
    def test_simple(a):
        assert True
