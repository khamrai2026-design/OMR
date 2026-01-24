import sqlite3
conn = sqlite3.connect('omr_data.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(chapters)")
print(cursor.fetchall())
conn.close()
