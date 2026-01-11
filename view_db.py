import sqlite3
import json
import pandas as pd

# Connect to database
conn = sqlite3.connect('omr_data.db')

# Show all chapters
print("=" * 80)
print("📚 ALL CHAPTERS IN DATABASE")
print("=" * 80)

chapters_df = pd.read_sql_query("SELECT * FROM chapters", conn)

if not chapters_df.empty:
    for idx, row in chapters_df.iterrows():
        print(f"\n🔹 Chapter ID: {row['id']}")
        print(f"   Name: {row['chapter_name']}")
        print(f"   Questions: {row['num_questions']}")
        print(f"   Options: {row['num_options']}")
        print(f"   Created: {row['created_at']}")
        
        # Parse and display answers
        correct_answers = json.loads(row['correct_answers'])
        print(f"   Answers: {', '.join(str(a) for a in correct_answers)}")
else:
    print("No chapters found in database.")

# Show all attempts
print("\n" + "=" * 80)
print("📝 ALL ATTEMPTS IN DATABASE")
print("=" * 80)

attempts_df = pd.read_sql_query('''
    SELECT a.*, c.chapter_name 
    FROM attempts a
    JOIN chapters c ON a.chapter_id = c.id
    ORDER BY a.submitted_at DESC
''', conn)

if not attempts_df.empty:
    for idx, row in attempts_df.iterrows():
        print(f"\n🔸 Attempt ID: {row['id']}")
        print(f"   Student: {row['student_name']}")
        print(f"   Chapter: {row['chapter_name']}")
        print(f"   Score: {row['score']}/{row['total_questions']} ({row['score']/row['total_questions']*100:.1f}%)")
        print(f"   Attempt #: {row['attempt_number']}")
        print(f"   Submitted: {row['submitted_at']}")
        
        # Parse and display submitted answers
        submitted_answers = json.loads(row['submitted_answers'])
        print(f"   Answers: {', '.join(str(a) for a in submitted_answers)}")
else:
    print("No attempts found in database.")

print("\n" + "=" * 80)

conn.close()
