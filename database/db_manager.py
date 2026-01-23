"""
Database manager for handling all database operations.
"""
import sqlite3
from typing import List, Optional, Tuple
import pandas as pd
from contextlib import contextmanager

from models import Chapter, Attempt
from config import DATABASE_PATH


class DatabaseManager:
    """
    Manages all database operations for the OMR application.

    This class implements the Singleton pattern to ensure only one
    database connection manager exists throughout the application.
    """

    _instance = None

    def __new__(cls):
        """Implement Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the database manager."""
        if self._initialized:
            return
        self.db_path = str(DATABASE_PATH)
        self._initialized = True
        self.initialize_database()

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def initialize_database(self):
        """Initialize the database with required tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Create chapters table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chapter_name TEXT UNIQUE NOT NULL,
                    num_questions INTEGER NOT NULL,
                    num_options INTEGER NOT NULL,
                    correct_answers TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create attempts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chapter_id INTEGER NOT NULL,
                    student_name TEXT NOT NULL,
                    submitted_answers TEXT NOT NULL,
                    score REAL NOT NULL,
                    total_questions INTEGER NOT NULL,
                    attempt_number INTEGER NOT NULL,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chapter_id) REFERENCES chapters(id)
                )
            ''')

    # Chapter operations

    def save_chapter(self, chapter: Chapter) -> Tuple[bool, str]:
        """
        Save a chapter to the database.

        Args:
            chapter: Chapter instance to save

        Returns:
            Tuple of (success, message)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO chapters (chapter_name, num_questions, num_options, correct_answers)
                    VALUES (?, ?, ?, ?)
                ''', (
                    chapter.chapter_name,
                    chapter.num_questions,
                    chapter.num_options,
                    chapter.get_correct_answers_json()
                ))
                return True, "Chapter saved successfully!"
        except sqlite3.IntegrityError:
            return False, "Chapter already exists!"
        except Exception as e:
            return False, f"Error saving chapter: {str(e)}"

    def get_all_chapters(self) -> pd.DataFrame:
        """
        Get all chapters from the database.

        Returns:
            DataFrame containing all chapters
        """
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM chapters", conn)

    def get_chapter_by_name(self, chapter_name: str) -> Optional[Chapter]:
        """
        Get a chapter by its name.

        Args:
            chapter_name: Name of the chapter

        Returns:
            Chapter instance or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM chapters WHERE chapter_name = ?", (chapter_name,))
            row = cursor.fetchone()

            if row:
                return Chapter.from_db_row(row)
            return None

    def get_chapter_by_id(self, chapter_id: int) -> Optional[Chapter]:
        """
        Get a chapter by its ID.

        Args:
            chapter_id: ID of the chapter

        Returns:
            Chapter instance or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM chapters WHERE id = ?", (chapter_id,))
            row = cursor.fetchone()

            if row:
                return Chapter.from_db_row(row)
            return None

    # Attempt operations

    def save_attempt(self, attempt: Attempt) -> bool:
        """
        Save an attempt to the database.

        Args:
            attempt: Attempt instance to save

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO attempts 
                    (chapter_id, student_name, submitted_answers, score, total_questions, attempt_number)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    attempt.chapter_id,
                    attempt.student_name,
                    attempt.get_submitted_answers_json(),
                    attempt.score,
                    attempt.total_questions,
                    attempt.attempt_number
                ))
                return True
        except Exception as e:
            print(f"Error saving attempt: {str(e)}")
            return False

    def get_attempt_count(self, chapter_id: int, student_name: str) -> int:
        """
        Get the number of attempts for a student on a specific chapter.

        Args:
            chapter_id: ID of the chapter
            student_name: Name of the student

        Returns:
            Number of attempts
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM attempts 
                WHERE chapter_id = ? AND student_name = ?
            ''', (chapter_id, student_name))
            return cursor.fetchone()[0]

    def get_student_attempts(self, chapter_name: str, student_name: Optional[str] = None) -> pd.DataFrame:
        """
        Get all attempts for a chapter, optionally filtered by student.

        Args:
            chapter_name: Name of the chapter
            student_name: Optional student name filter

        Returns:
            DataFrame containing attempts
        """
        with self.get_connection() as conn:
            if student_name:
                query = '''
                    SELECT a.*, c.chapter_name 
                    FROM attempts a
                    JOIN chapters c ON a.chapter_id = c.id
                    WHERE c.chapter_name = ? AND a.student_name = ?
                    ORDER BY a.submitted_at DESC
                '''
                return pd.read_sql_query(query, conn, params=(chapter_name, student_name))
            else:
                query = '''
                    SELECT a.*, c.chapter_name 
                    FROM attempts a
                    JOIN chapters c ON a.chapter_id = c.id
                    WHERE c.chapter_name = ?
                    ORDER BY a.submitted_at DESC
                '''
                return pd.read_sql_query(query, conn, params=(chapter_name,))

    def get_all_attempts(self) -> pd.DataFrame:
        """
        Get all attempts from the database.

        Returns:
            DataFrame containing all attempts
        """
        with self.get_connection() as conn:
            query = '''
                SELECT a.*, c.chapter_name 
                FROM attempts a
                JOIN chapters c ON a.chapter_id = c.id
            '''
            return pd.read_sql_query(query, conn)
