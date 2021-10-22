from configparser import ConfigParser
import pkgutil
from datetime import datetime

test_email = 'a@a.com'
datetime1 = datetime(year=2021, month=10, day=19, hour=10, minute=10)
datetime2 = datetime(year=2021, month=10, day=20, hour=10, minute=10)
datetime3 = datetime(year=2021, month=10, day=21, hour=10, minute=10)
datetime4 = datetime(year=2021, month=10, day=22, hour=10, minute=10)

datetime5 = datetime(year=2021, month=10, day=26, hour=10, minute=10)
datetime6 = datetime(year=2021, month=11, day=16, hour=10, minute=10)
datetime7 = datetime(year=2022, month=10, day=19, hour=10, minute=10)

datetime8 = datetime(year=2021, month=10, day=29, hour=10, minute=10)
datetime9 = datetime(year=2021, month=11, day=5, hour=10, minute=10)

weird_activity = 'weird activity that for sure is not in the db'
weird_recurrence = 'YDWIDWHU'
    
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
