#!/usr/bin/env python
"""Database migration script"""
import sqlite3

DATABASE = 'omr_data.db'

def migrate_db():
    """Add time_taken column if it doesn't exist"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Check if attempts table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attempts'")
    if not c.fetchone():
        print("✗ Attempts table doesn't exist. Run init_db first.")
        conn.close()
        return
    
    # Check if time_taken column exists
    c.execute("PRAGMA table_info(attempts)")
    columns = [row[1] for row in c.fetchall()]
    
    if 'time_taken' not in columns:
        print("Adding time_taken column to attempts table...")
        c.execute('ALTER TABLE attempts ADD COLUMN time_taken INTEGER DEFAULT 0')
        conn.commit()
        print("✓ Migration completed successfully")
    else:
        print("✓ time_taken column already exists")
    
    conn.close()

if __name__ == '__main__':
    migrate_db()
