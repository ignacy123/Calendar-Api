import psycopg2

host = "localhost"
port = 5432

def set_host(new_host):
    host = new_host

def set_port(new_port):
    port = new_port
    
def get_conn():
    conn = psycopg2.connect(
    host=host,
    database="ignacy",
    user="ignacy",
    password="root",
    port=port)
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
    print(name)
    cur.execute("SELECT * FROM activities WHERE name = %s", (name, ))
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise NoSuchActivityException("Getting id of non-existent activity")
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
    #when attempting to choose an activity that is already favourite, just ignore
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
    print("DELETE FROM fav_activities WHERE email_id = {} AND activity_id = {}".format(email_id, activity_id))
    cur.execute("DELETE FROM fav_activities WHERE email_id = %s AND activity_id = %s", (email_id, activity_id))
    conn.commit()
    cur.close()
    conn.close()


class NoSuchActivityException(Exception):
    """A non-existant activity is requested"""
