import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

con = create_connection('./database.db')

def init_db():
    c = con.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            owner text,
            trans text,
            symbol text,
            qty real,
            price real
        );
    """)
    con.commit()

# def buy():
#     c =
