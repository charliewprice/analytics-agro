import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd

def kanjiDbConnect(dbhost, dbport, dbname, dbuser, dbpass):
  conn_str = "host={0} port={1} dbname={2} user={3} password={4}".format(dbhost, dbport, dbname, dbuser, dbpass)
  try:
    conn = pg.connect(conn_str)
    print(\"Welcome to Jupyter Notebook.  You are connected to the Kanji database!\")
    return conn
  except pg.OperationalError:
    print(\"You are not connected to the database.\")
    return None"
