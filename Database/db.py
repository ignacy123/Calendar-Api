#!/bin/python3

import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="ignacy",
    user="ignacy",
    password="root",
    port=5432)
    
cur = conn.cursor()

cur.execute("SELECT name FROM activities")

print("Row count:", cur.rowcount)

rows = cur.fetchall()
    
for row in rows:
    print(row[0])
    row = cur.fetchone()
    
cur.close()

cur = conn.cursor()

#cur.execute("INSERT INTO fav_activities (activity_id) VALUES (1)")

cur.execute("DELETE FROM fav_activities WHERE activity_id = 1")

cur.close()

conn.commit()

conn.close()
