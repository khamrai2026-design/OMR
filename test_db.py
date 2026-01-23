import sqlite3
import json

conn = sqlite3.connect('omr_data.db')
c = conn.cursor()

# Check chapters
c.execute('SELECT COUNT(*) FROM chapters')
count = c.fetchone()[0]
print(f"Total chapters in database: {count}")

if count > 0:
    c.execute('SELECT * FROM chapters')
    chapters = c.fetchall()
    for ch in chapters:
        print(f"  - ID: {ch[0]}, Name: {ch[1]}, Questions: {ch[2]}, Options: {ch[3]}")
else:
    print("No chapters found in database!")

# Check table structure
c.execute("PRAGMA table_info(chapters)")
columns = c.fetchall()
print("\nChapters table structure:")
for col in columns:
    print(f"  - {col[1]}: {col[2]}")

conn.close()
