import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO ACCOUNTS (username, password, type) VALUES (?, ?, ?)",
            ('admin', 'admin', 'admin')
            )

connection.commit()
connection.close()
