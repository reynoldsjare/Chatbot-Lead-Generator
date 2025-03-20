import sqlite3

conn = sqlite3.connect("leads.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        message TEXT
    )
''')

conn.commit()
conn.close()
