#!/usr/bin/env python
"""Check database schema"""
import sqlite3

DATABASE = 'omr_data.db'

def check_schema():
    """Check table schema"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Check attempts table columns
    c.execute("PRAGMA table_info(attempts)")
    columns = c.fetchall()
    
    print("Attempts table columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == '__main__':
    check_schema()
