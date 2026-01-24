"""
Database migration script to update omr_data.db with new schema.
Adds subjects master table and subject_id to chapters table.
"""
import sqlite3
from pathlib import Path
from config import DATABASE_PATH

def migrate_database():
    """Migrate the database to include subjects table and subject_id in chapters."""
    db_path = str(DATABASE_PATH)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Step 1: Create subjects table if it doesn't exist
        print("Creating subjects table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ Subjects table created/verified")
        
        # Step 2: Check if chapters table has subject_id column
        cursor.execute("PRAGMA table_info(chapters)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'subject_id' not in columns:
            print("Adding subject_id to chapters table...")
            
            # Step 3: Rename old chapters table
            cursor.execute("ALTER TABLE chapters RENAME TO chapters_old")
            
            # Step 4: Create new chapters table with subject_id
            cursor.execute('''
                CREATE TABLE chapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id INTEGER NOT NULL,
                    chapter_name TEXT UNIQUE NOT NULL,
                    num_questions INTEGER NOT NULL,
                    num_options INTEGER NOT NULL,
                    correct_answers TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id)
                )
            ''')
            
            # Step 5: Create default subject if needed
            cursor.execute("SELECT COUNT(*) FROM subjects")
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO subjects (subject_name, description)
                    VALUES (?, ?)
                ''', ('Default Subject', 'Default subject for existing chapters'))
                default_subject_id = cursor.lastrowid
            else:
                cursor.execute("SELECT id FROM subjects LIMIT 1")
                default_subject_id = cursor.fetchone()[0]
            
            # Step 6: Copy data from old table to new table
            cursor.execute('''
                INSERT INTO chapters (subject_id, chapter_name, num_questions, num_options, correct_answers, created_at)
                SELECT ?, chapter_name, num_questions, num_options, correct_answers, created_at
                FROM chapters_old
            ''', (default_subject_id,))
            
            # Step 7: Drop old table
            cursor.execute("DROP TABLE chapters_old")
            
            print("✓ subject_id added to chapters table")
            print(f"✓ All existing chapters assigned to 'Default Subject' (ID: {default_subject_id})")
        else:
            print("✓ Chapters table already has subject_id column")
        
        # Verify attempts table has time_taken columns
        cursor.execute("PRAGMA table_info(attempts)")
        attempt_columns = [col[1] for col in cursor.fetchall()]
        
        if 'time_taken' not in attempt_columns:
            print("Adding time_taken to attempts table...")
            cursor.execute("ALTER TABLE attempts ADD COLUMN time_taken INTEGER DEFAULT 0")
            print("✓ time_taken added to attempts table")
        
        if 'start_time' not in attempt_columns:
            print("Adding start_time to attempts table...")
            cursor.execute("ALTER TABLE attempts ADD COLUMN start_time TIMESTAMP")
            print("✓ start_time added to attempts table")
        
        if 'end_time' not in attempt_columns:
            print("Adding end_time to attempts table...")
            cursor.execute("ALTER TABLE attempts ADD COLUMN end_time TIMESTAMP")
            print("✓ end_time added to attempts table")
        
        conn.commit()
        print("\n✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during migration: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("OMR Database Migration")
    print("=" * 60)
    success = migrate_database()
    print("=" * 60)
    exit(0 if success else 1)
