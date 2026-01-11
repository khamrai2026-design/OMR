import sqlite3
import json

# Connect to database
conn = sqlite3.connect('omr_data.db')
c = conn.cursor()

# The correct answers in LETTER format (A, B, C, D)
# Original numeric: [3, 4, 4, 3, 1, 3, 2, 3, 2, 3, 4, 3, 2, 3, 4, 1, 4, 4, 2, 1]
correct_answers = ['C', 'D', 'D', 'C', 'A', 'C', 'B', 'C', 'B', 'C', 'D', 'C', 'B', 'C', 'D', 'A', 'D', 'D', 'B', 'A']

# Chapter details
chapter_name = "Sample Chapter - 20 Questions"
num_questions = 20
num_options = 4

# Insert the chapter
try:
    c.execute('''INSERT INTO chapters (chapter_name, num_questions, num_options, correct_answers)
                 VALUES (?, ?, ?, ?)''',
              (chapter_name, num_questions, num_options, json.dumps(correct_answers)))
    conn.commit()
    print(f"✅ Successfully added chapter: {chapter_name}")
    print(f"   Questions: {num_questions}")
    print(f"   Options: {num_options}")
    print(f"   Answers: {', '.join(correct_answers)}")
    
except sqlite3.IntegrityError:
    print(f"❌ Chapter '{chapter_name}' already exists!")
    print("   Deleting old chapter and creating new one...")
    
    # Delete the old chapter
    c.execute("DELETE FROM chapters WHERE chapter_name = ?", (chapter_name,))
    
    # Insert the new chapter
    c.execute('''INSERT INTO chapters (chapter_name, num_questions, num_options, correct_answers)
                 VALUES (?, ?, ?, ?)''',
              (chapter_name, num_questions, num_options, json.dumps(correct_answers)))
    conn.commit()
    print(f"✅ Successfully updated chapter: {chapter_name}")
    print(f"   Questions: {num_questions}")
    print(f"   Options: {num_options}")
    print(f"   Answers: {', '.join(correct_answers)}")

conn.close()
