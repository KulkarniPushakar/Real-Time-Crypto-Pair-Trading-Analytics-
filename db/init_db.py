import sqlite3

conn = sqlite3.connect("analytics.db")
with open("db/schema.sql") as f:
    conn.executescript(f.read())
conn.close()

print("SQLite database initialized")
