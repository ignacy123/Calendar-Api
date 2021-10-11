import psycopg2
from configparser import ConfigParser

def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db
    
def get_conn():
    params = config()
    conn = psycopg2.connect(**params)
    return conn
    
def all_activities():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM activities")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def fav_activities(email):
    email_id = get_email_id(email)
    
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT activities.id, name FROM fav_activities LEFT OUTER JOIN activities ON activities.id = fav_activities.activity_id WHERE email_id = %s;", (email_id, ))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
    

def get_activity_id(name):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM activities WHERE name = %s", (name, ))
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise NoSuchActivityException("Getting id of a non-existent activity")
    id = cur.fetchone()[0]
    return id

def get_email_id(email):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM email WHERE email = %s", (email, ))
    if cur.rowcount == 0:
        cur.execute("INSERT INTO email (email) VALUES (%s)", (email, ))
        conn.commit()
        cur.execute("SELECT * FROM email WHERE email = %s", (email, ))
    id = cur.fetchone()[0]
    cur.close()
    conn.close()
    return id

def new_fav(email, name):
    activity_id = get_activity_id(name)
    email_id = get_email_id(email)
    conn = get_conn()
    cur = conn.cursor()
    #when attempting to choose an activity that is already a favourite, just ignore
    try:
        cur.execute("INSERT INTO fav_activities (email_id, activity_id) VALUES (%s, %s)", (email_id, activity_id))
    except psycopg2.errors.UniqueViolation as e:
        pass
    conn.commit()
    cur.close()
    conn.close()

def delete_fav(email, name):
    activity_id = get_activity_id(name)
    email_id = get_email_id(email)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM fav_activities WHERE email_id = %s AND activity_id = %s", (email_id, activity_id))
    conn.commit()
    cur.close()
    conn.close()

def add_event(email, start_date, end_date, name):
    activity_id = get_activity_id(name)
    email_id = get_email_id(email)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO single_events (email_id, activity_id, start_time, end_time) VALUES (%s, %s, %s, %s)", (email_id, activity_id, start_date, end_date))
    conn.commit()
    cur.close()
    conn.close()
    
class NoSuchActivityException(Exception):
    """A non-existant activity is requested"""
