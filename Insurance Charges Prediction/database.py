import sqlite3
from sqlite3 import Error

def get_db_connection():
    conn = None
    try:
        conn = sqlite3.connect('userdata.db')
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            yield conn
            conn.close()