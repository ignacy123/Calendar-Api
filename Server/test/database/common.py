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

datetime10 = datetime(year=2021, month=10, day=19, hour=12, minute=10)

datetime11 = datetime(year=2021, month=11, day=3, hour=10, minute=10)

datetime12 = datetime(year=2022, month=4, day=30, hour=10, minute=10)

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

def date_minus_one_month(date):
    prev_month = date.month-1 if date.month > 1 else 12
    year_of_prev_month = date.year if date.month > 1 else date.year - 1
    return date.replace(year = year_of_prev_month, month = prev_month)

def date_minus_x_months(date, x):
    for _ in range(x):
        date = date_minus_one_month(date)
    return date

def date_plus_one_month(date):
    next_month = date.month+1 if date.month < 12 else 1
    year_of_next_month = date.year if date.month < 12 else date.year + 1
    return date.replace(year = year_of_next_month, month = next_month)

def date_plus_x_months(date, x):
    for _ in range(x):
        date = date_plus_one_month(date)
    return date

def date_minus_x_years(date, x):
    return date.replace(year = date.year-x)

def date_plus_x_years(date, x):
    return date.replace(year = date.year+x)
    
