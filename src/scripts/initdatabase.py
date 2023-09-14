import sqlite3
import os

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR,'catFeed.sqlite3')
    conn = sqlite3.connect(db_path)
    with open('schema.sql','r') as sql_file:
        sql_script=sql_file.read()
    cur = conn.cursor()
    print(sql_script)
    cur.executescript(sql_script)
    conn.commit()
    print(cur.fetchall())
    conn.close()
except KeyboardInterrupt:
    print("exited")
