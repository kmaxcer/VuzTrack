import sqlite3
from db.config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT * FROM parsing_sources")
for row in cur.fetchall():
    print(row)
    print()