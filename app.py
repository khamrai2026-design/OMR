
import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import json
import os
from io import BytesIO
from contextlib import contextmanager

# ==================== Database Manager Class ====================


class DatabaseManager:
    """Handles all SQLite database operations with OOP principles"""
    
    def __init__(self, db_path: str = 'omr_data.db'):
        """Initialize database manager with database path"""
        self.db_path = db_path
        self.init_db()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
        finally:
            conn.close()
    
    def init_db(self):
        """Initialize the SQLite database with required tables"""
        with self._get_connection() as conn:
            c = conn.cursor()
            
            # Create chapters table
            c.execute('''CREATE TABLE IF NOT EXISTS chapters
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          chapter_name TEXT UNIQUE NOT NULL,
                          num_questions INTEGER NOT NULL,
                          num_options INTEGER NOT NULL,
                          correct_answers TEXT NOT NULL,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            # Create attempts table
            c.execute('''CREATE TABLE IF NOT EXISTS attempts
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          chapter_id INTEGER NOT NULL,
                          student_name TEXT NOT NULL,
                          submitted_answers TEXT NOT NULL,
                          score REAL NOT NULL,
                          total_questions INTEGER NOT NULL,
                          attempt_number INTEGER NOT NULL,
                          submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY (chapter_id) REFERENCES chapters(id))''')
            
            conn.commit()
    
    def save_chapter(self, chapter_name: str, num_questions: int, 
                     num_options: int, correct_answers: list) -> tuple:
        """
        Save a new chapter to the database
        
        Args:
            chapter_name: Name of the chapter
            num_questions: Number of questions
            num_options: Number of options per question
            correct_answers: List of correct answers
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute('''INSERT INTO chapters 
                             (chapter_name, num_questions, num_options, correct_answers)
                             VALUES (?, ?, ?, ?)''',
                          (chapter_name, num_questions, num_options, json.dumps(correct_answers)))
                conn.commit()
                return True, "Chapter saved successfully!"
        except sqlite3.IntegrityError:
            return False, "Chapter already exists!"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_all_chapters(self) -> pd.DataFrame:
        """Retrieve all chapters from database"""
        with self._get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM chapters ORDER BY created_at DESC", conn)
            return df
    
    def get_chapter_by_name(self, chapter_name: str) -> tuple:
        """
        Get chapter details by name
        
        Args:
            chapter_name: Name of the chapter to retrieve
            
        Returns:
            Tuple of chapter data or None if not found
        """
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM chapters WHERE chapter_name = ?", (chapter_name,))
            result = c.fetchone()
            return tuple(result) if result else None
    
    def get_attempt_count(self, chapter_id: int, student_name: str) -> int:
        """
        Get the number of attempts for a student on a specific chapter
        
        Args:
            chapter_id: ID of the chapter
            student_name: Name of the student
            
        Returns:
            Count of attempts
        """
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT COUNT(*) FROM attempts
                         WHERE chapter_id = ? AND student_name = ?''',
                      (chapter_id, student_name))
            count = c.fetchone()[0]
            return count
    
    def save_attempt(self, chapter_id: int, student_name: str, 
                     submitted_answers: list, score: float, 
                     total_questions: int, attempt_number: int) -> bool:
        """
        Save a student's exam attempt
        
        Args:
            chapter_id: ID of the chapter
            student_name: Name of the student
            submitted_answers: List of submitted answers
            score: Score obtained
            total_questions: Total number of questions
            attempt_number: Attempt number
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                c = conn.cursor()
                c.execute('''INSERT INTO attempts
                             (chapter_id, student_name, submitted_answers,
                              score, total_questions, attempt_number)
                             VALUES (?, ?, ?, ?, ?, ?)''',
                          (chapter_id, student_name, json.dumps(submitted_answers), 
                           score, total_questions, attempt_number))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving attempt: {str(e)}")
            return False
    
    def get_student_attempts(self, chapter_name: str, student_name: str = None) -> pd.DataFrame:
        """
        Get all attempts for a chapter, optionally filtered by student
        
        Args:
            chapter_name: Name of the chapter
            student_name: Optional filter by student name
            
        Returns:
            DataFrame of attempts
        """
        with self._get_connection() as conn:
            if student_name:
                query = '''SELECT a.*, c.chapter_name
                           FROM attempts a
                           JOIN chapters c ON a.chapter_id = c.id
                           WHERE c.chapter_name = ? AND a.student_name = ?
                           ORDER BY a.submitted_at DESC'''
                df = pd.read_sql_query(query, conn, params=(chapter_name, student_name))
            else:
                query = '''SELECT a.*, c.chapter_name
                           FROM attempts a
                           JOIN chapters c ON a.chapter_id = c.id
                           WHERE c.chapter_name = ?
                           ORDER BY a.submitted_at DESC'''
                df = pd.read_sql_query(query, conn, params=(chapter_name,))
            
            return df
    
    def get_all_attempts(self) -> pd.DataFrame:
        """Get all attempts across all chapters"""
        with self._get_connection() as conn:
            query = '''SELECT a.*, c.chapter_name 
                       FROM attempts a
                       JOIN chapters c ON a.chapter_id = c.id
                       ORDER BY a.submitted_at DESC'''
            df = pd.read_sql_query(query, conn)
            return df
    
    def get_student_statistics(self) -> pd.DataFrame:
        """Get aggregated statistics for all students"""
        with self._get_connection() as conn:
            query = '''SELECT student_name, COUNT(id) as total_attempts,
                              SUM(score) as total_score, SUM(total_questions) as total_questions
                       FROM attempts
                       GROUP BY student_name
                       ORDER BY total_score DESC'''
            df = pd.read_sql_query(query, conn)
            return df
    
    def get_chapter_statistics(self) -> pd.DataFrame:
        """Get aggregated statistics for all chapters"""
        with self._get_connection() as conn:
            query = '''SELECT c.chapter_name, COUNT(a.id) as total_attempts,
                              AVG(a.score) as avg_score, AVG(a.total_questions) as avg_total,
                              COUNT(DISTINCT a.student_name) as unique_students
                       FROM chapters c
                       LEFT JOIN attempts a ON c.id = a.chapter_id
                       GROUP BY c.id
                       ORDER BY total_attempts DESC'''
            df = pd.read_sql_query(query, conn)
            return df


# ==================== Helper Functions ====================

def get_option_letters(num_options: int) -> list:
    """Get list of option letters based on number of options"""
    return [chr(65 + i) for i in range(num_options)]  # A, B, C, D, E, F


def calculate_score(correct_answers: list, submitted_answers: list) -> int:
    """Calculate score based on correct and submitted answers"""
    correct_count = 0
    for correct, submitted in zip(correct_answers, submitted_answers):
        if correct == submitted:
            correct_count += 1
    return correct_count


def create_excel_download(student_name, chapter_name, score, total_questions,
                          percentage, attempt_number, submitted_answers,
                          correct_answers, submitted_at=None):
    """Create Excel file with exam details and answer comparison"""

    # Create a BytesIO buffer for the Excel file
    output = BytesIO()

    # Create Excel writer
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book

        # Format for headers
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#0d6efd',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        # Format for correct answers
        correct_format = workbook.add_format({
            'bg_color': '#d4edda',
            'border': 1
        })

        # Format for incorrect answers
        incorrect_format = workbook.add_format({
            'bg_color': '#f8d7da',
            'border': 1
        })

        # Format for summary
        summary_format = workbook.add_format({
            'bold': True,
            'border': 1
        })

        # Format for general cells
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'center'
        })

        # ========== Sheet 1: Exam Summary ==========
        summary_data = {
            'Field': [
                'Student Name',
                'Chapter Name',
                'Date & Time',
                'Score',
                'Total Questions',
                'Percentage',
                'Attempt Number'
            ],
            'Value': [
                student_name,
                chapter_name,
                submitted_at if submitted_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                f"{score}/{total_questions}",
                total_questions,
                f"{percentage:.2f}%",
                attempt_number
            ]
        }

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Exam Summary', index=False)

        summary_sheet = writer.sheets['Exam Summary']
        summary_sheet.set_column('A:A', 20)
        summary_sheet.set_column('B:B', 30)

        # Apply formatting to header
        for col_num, value in enumerate(summary_df.columns.values):
            summary_sheet.write(0, col_num, value, header_format)

        # Apply formatting to data
        for row_num in range(1, len(summary_df) + 1):
            for col_num in range(len(summary_df.columns)):
                summary_sheet.write(row_num, col_num,
                                    summary_df.iloc[row_num-1, col_num],
                                    cell_format)

        # ========== Sheet 2: Answer Comparison ==========
        comparison_data = []
        for i in range(len(submitted_answers)):
            is_correct = submitted_answers[i] == correct_answers[i]
            comparison_data.append({
                'Question No.': i + 1,
                'Your Answer': submitted_answers[i] if submitted_answers[i] else 'Not Answered',
                'Correct Answer': correct_answers[i],
                'Status': 'Correct' if is_correct else 'Incorrect',
                'Remarks': '✓' if is_correct else '✗'
            })

        comparison_df = pd.DataFrame(comparison_data)
        comparison_df.to_excel(
            writer, sheet_name='Answer Comparison', index=False)

        comparison_sheet = writer.sheets['Answer Comparison']
        comparison_sheet.set_column('A:A', 15)  # Question No.
        comparison_sheet.set_column('B:B', 15)  # Your Answer
        comparison_sheet.set_column('C:C', 15)  # Correct Answer
        comparison_sheet.set_column('D:D', 12)  # Status
        comparison_sheet.set_column('E:E', 10)  # Remarks

        # Apply formatting to header
        for col_num, value in enumerate(comparison_df.columns.values):
            comparison_sheet.write(0, col_num, value, header_format)

        # Apply conditional formatting to data
        for row_num in range(1, len(comparison_df) + 1):
            for col_num in range(len(comparison_df.columns)):
                cell_value = comparison_df.iloc[row_num-1, col_num]

                # Apply different formats based on status
                if col_num == 3:  # Status column
                    if cell_value == 'Correct':
                        comparison_sheet.write(
                            row_num, col_num, cell_value, correct_format)
                    else:
                        comparison_sheet.write(
                            row_num, col_num, cell_value, incorrect_format)
                elif col_num == 4:  # Remarks column
                    if cell_value == '✓':
                        comparison_sheet.write(
                            row_num, col_num, cell_value, correct_format)
                    else:
                        comparison_sheet.write(
                            row_num, col_num, cell_value, incorrect_format)
                else:
                    comparison_sheet.write(
                        row_num, col_num, cell_value, cell_format)

        # ========== Sheet 3: Performance Analysis ==========
        analysis_data = {
            'Metric': [
                'Total Questions',
                'Correct Answers',
                'Incorrect Answers',
                'Not Answered',
                'Score',
                'Percentage',
                'Accuracy Rate'
            ],
            'Value': [
                total_questions,
                score,
                total_questions - score,
                sum(1 for ans in submitted_answers if ans is None),
                f"{score}/{total_questions}",
                f"{percentage:.2f}%",
                f"{(score/total_questions*100):.2f}%"
            ]
        }

        analysis_df = pd.DataFrame(analysis_data)
        analysis_df.to_excel(
            writer, sheet_name='Performance Analysis', index=False)

        analysis_sheet = writer.sheets['Performance Analysis']
        analysis_sheet.set_column('A:A', 25)
        analysis_sheet.set_column('B:B', 20)

        # Apply formatting to header
        for col_num, value in enumerate(analysis_df.columns.values):
            analysis_sheet.write(0, col_num, value, header_format)

        # Apply formatting to data
        for row_num in range(1, len(analysis_df) + 1):
            for col_num in range(len(analysis_df.columns)):
                analysis_sheet.write(row_num, col_num,
                                     analysis_df.iloc[row_num-1, col_num],
                                     summary_format if col_num == 0 else cell_format)

        # ========== Sheet 4: Question-wise Detail ==========
        detail_data = []
        for i in range(len(submitted_answers)):
            is_correct = submitted_answers[i] == correct_answers[i]
            detail_data.append({
                'Q.No': i + 1,
                'Your Answer': submitted_answers[i] if submitted_answers[i] else 'N/A',
                'Correct Answer': correct_answers[i],
                'Is Correct': 'Yes' if is_correct else 'No',
                'Points': 1 if is_correct else 0,
                'Feedback': 'Well done!' if is_correct else 'Review this topic'
            })

        detail_df = pd.DataFrame(detail_data)
        detail_df.to_excel(writer, sheet_name='Question Details', index=False)

        detail_sheet = writer.sheets['Question Details']
        detail_sheet.set_column('A:A', 8)   # Q.No
        detail_sheet.set_column('B:B', 12)  # Your Answer
        detail_sheet.set_column('C:C', 12)  # Correct Answer
        detail_sheet.set_column('D:D', 10)  # Is Correct
        detail_sheet.set_column('E:E', 8)   # Points
        detail_sheet.set_column('F:F', 25)  # Feedback

        # Apply formatting to header
        for col_num, value in enumerate(detail_df.columns.values):
            detail_sheet.write(0, col_num, value, header_format)

        # Apply conditional formatting to data
        for row_num in range(1, len(detail_df) + 1):
            for col_num in range(len(detail_df.columns)):
                cell_value = detail_df.iloc[row_num-1, col_num]

                # Apply different formats based on correctness
                if col_num == 3:  # Is Correct column
                    if cell_value == 'Yes':
                        detail_sheet.write(
                            row_num, col_num, cell_value, correct_format)
                    else:
                        detail_sheet.write(
                            row_num, col_num, cell_value, incorrect_format)
                elif col_num == 4:  # Points column
                    if cell_value == 1:
                        detail_sheet.write(
                            row_num, col_num, cell_value, correct_format)
                    else:
                        detail_sheet.write(
                            row_num, col_num, cell_value, incorrect_format)
                else:
                    detail_sheet.write(
                        row_num, col_num, cell_value, cell_format)

    # Get the Excel data
    excel_data = output.getvalue()
    return excel_data

# Streamlit UI


def main():
    st.set_page_config(page_title="OMR Sheet Submission System",
                       page_icon="📝", layout="wide")

    # Initialize database manager
    db = DatabaseManager('omr_data.db')
    
    # Store db manager in session state for use across pages
    if 'db' not in st.session_state:
        st.session_state.db = db
    else:
        db = st.session_state.db
    
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    
    <style>
    /* Modern Design System */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #ec4899;
        --accent: #8b5cf6;
        --success: #10b981;
        --error: #ef4444;
        --warning: #f59e0b;
        --info: #3b82f6;
        --text-main: #0f172a;
        --text-muted: #64748b;
        --bg-light: #f8fafc;
        --border: rgba(0, 0, 0, 0.08);
        --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.08), 0 1px 2px 0 rgba(0, 0, 0, 0.04);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f0f9ff 50%, #f5f3ff 100%) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        color: var(--text-main) !important;
    }

    h1 { 
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em !important;
        color: var(--text-main) !important;
        margin-bottom: 1rem !important;
    }

    h2 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        color: var(--text-main) !important;
        margin-bottom: 1.5rem !important;
    }

    h3 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: var(--text-main) !important;
    }

    /* Modern Card Styling */
    .glass-card {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        box-shadow: var(--shadow-md) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-bottom: 2rem !important;
    }

    .glass-card:hover {
        box-shadow: var(--shadow-lg) !important;
        transform: translateY(-2px) !important;
    }

    /* Modern Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4) !important;
    }

    /* Input Styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    textarea {
        background-color: white !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
        outline: none !important;
    }

    /* Modern Radio Buttons */
    div[data-baseweb="radio"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 12px !important;
    }

    div[data-baseweb="radio"] label {
        background: white !important;
        border: 2px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 12px 20px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        box-shadow: var(--shadow-sm) !important;
    }

    div[data-baseweb="radio"] label:hover {
        border-color: var(--primary) !important;
        background: rgba(99, 102, 241, 0.05) !important;
        transform: translateY(-1px) !important;
    }

    div[data-baseweb="radio"] label[data-checked="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border-color: var(--primary) !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
    }

    /* Metric Cards */
    .metric-card {
        background: white !important;
        border-radius: 14px !important;
        padding: 1.75rem !important;
        border: 1px solid var(--border) !important;
        box-shadow: var(--shadow-sm) !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--accent));
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .metric-card:hover {
        border-color: var(--primary) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-4px) !important;
    }

    .metric-card:hover::before {
        opacity: 1;
    }

    .metric-value {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        line-height: 1 !important;
        margin-bottom: 0.5rem !important;
    }

    .metric-label {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: var(--text-muted) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
    }

    /* Status Badges */
    .badge {
        padding: 6px 14px !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
    }

    .bg-success { background: rgba(16, 185, 129, 0.1) !important; color: var(--success) !important; }
    .bg-danger { background: rgba(239, 68, 68, 0.1) !important; color: var(--error) !important; }
    .bg-warning { background: rgba(245, 158, 11, 0.1) !important; color: var(--warning) !important; }
    .bg-info { background: rgba(59, 130, 246, 0.1) !important; color: var(--info) !important; }

    /* Alert Styling */
    .stAlert {
        background: white !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 1.25rem !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* Main Container */
    .block-container {
        max-width: 1400px !important;
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
    }

    /* Table Styling */
    .table {
        font-size: 0.95rem !important;
        border-collapse: collapse !important;
    }

    .table thead {
        background: rgba(0, 0, 0, 0.02) !important;
        border-bottom: 2px solid var(--border) !important;
    }

    .table thead th {
        color: var(--text-muted) !important;
        font-weight: 700 !important;
        padding: 1rem !important;
        letter-spacing: 0.05em !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
    }

    .table tbody td {
        padding: 1rem !important;
        border-bottom: 1px solid var(--border) !important;
        color: var(--text-main) !important;
    }

    .table tbody tr:hover {
        background: rgba(0, 0, 0, 0.02) !important;
    }

    /* Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px !important;
        border-bottom: 1px solid var(--border) !important;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0 !important;
        padding: 12px 24px !important;
        border: none !important;
        font-weight: 600 !important;
    }

    .stTabs [aria-selected="true"] {
        border-bottom: 2px solid var(--primary) !important;
        color: var(--primary) !important;
    }

    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.05);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-dark);
    }

    /* Animations */
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    .glass-card {
        animation: slideUp 0.4s ease-out;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        h1 { font-size: 1.75rem !important; }
        h2 { font-size: 1.5rem !important; }
        .glass-card { padding: 1.5rem !important; }
        .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

    # Modern Navigation Header
    st.markdown("""
    <div style="
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(0, 0, 0, 0.08);
        padding: 1.5rem 2rem;
        margin: -2rem -2rem 2rem -2rem;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    ">
        <div style="text-align: center;">
            <h1 style="
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 2.5rem;
                margin-bottom: 0.25rem;
            ">📝 OMR Digital Suite</h1>
            <p style="color: #64748b; font-size: 0.95rem; margin: 0;">Smart Examination & Analytics Platform</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Create modern navigation using columns
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    
    current_page = st.session_state.get("current_page", "Exam")
    
    with nav_col1:
        if st.button("📝 Exam", use_container_width=True, 
                     key="nav_exam",
                     help="Take a test"):
            st.session_state.current_page = "Exam"
            st.rerun()
    
    with nav_col2:
        if st.button("📊 View Results", use_container_width=True,
                     key="nav_results",
                     help="View your test results"):
            st.session_state.current_page = "View Results"
            st.rerun()
    
    with nav_col3:
        if st.button("📈 Analytics", use_container_width=True,
                     key="nav_analytics",
                     help="View analytics dashboard"):
            st.session_state.current_page = "Analytics"
            st.rerun()

    st.markdown('<div style="margin-bottom: 2rem;"></div>', unsafe_allow_html=True)

    if st.session_state.current_page == "Exam":
        submit_omr_page()
    elif st.session_state.current_page == "View Results":
        view_results_page()
    elif st.session_state.current_page == "Analytics":
        analytics_page()


def submit_omr_page():
    """Page to submit exam"""
    db = st.session_state.db
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 3rem;
        color: white;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 40px rgba(99, 102, 241, 0.2);
    ">
        <div style="position: absolute; top: -10%; right: -5%; width: 300px; height: 300px; background: rgba(255,255,255,0.1); border-radius: 50%;"></div>
        <div style="position: relative; z-index: 1;">
            <span style="background: rgba(255,255,255,0.2); padding: 6px 16px; border-radius: 50px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;">📝 Smart Examination</span>
            <h2 style="color: white !important; font-size: 2.5rem; font-weight: 800; margin-top: 1rem; margin-bottom: 0.5rem;">Take a Test</h2>
            <p style="font-size: 1.1rem; opacity: 0.95; font-weight: 500; max-width: 600px; margin: 0;">Choose your chapter and start testing to identify areas for improvement.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Get all chapters
    chapters_df = db.get_all_chapters()

    if chapters_df.empty:
        st.markdown("""
        <div style="
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            color: #b91c1c;
        ">
            <strong>⚠️ No chapters available</strong><br>
            Please create a chapter first to get started!
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("""<div class="glass-card">""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:
        student_name = st.text_input("✍️ Student Name", value="Arin Khamrai",
                                     help="Enter your full name",
                                     placeholder="Your name")

    with col2:
        chapter_name = st.selectbox(
            "📚 Select Chapter",
            options=chapters_df['chapter_name'].tolist(),
            help="Choose the chapter for the test"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    if chapter_name:
        # Get chapter details
        chapter = db.get_chapter_by_name(chapter_name)
        chapter_id, _, num_questions, num_options, correct_answers_json, _ = chapter
        correct_answers = json.loads(correct_answers_json)

        # Display attempt count
        if student_name:
            attempt_count = db.get_attempt_count(chapter_id, student_name)
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
                border: 1px solid rgba(99, 102, 241, 0.3);
                border-radius: 12px;
                padding: 1.25rem;
                color: #0f172a;
                margin-bottom: 2rem;
            ">
                <strong style="color: #6366f1;">#{attempt_count + 1}</strong> attempt for <strong>{student_name}</strong> on <strong>{chapter_name}</strong>
            </div>
            """, unsafe_allow_html=True)

        option_letters = get_option_letters(num_options)

        st.markdown("""<div class="glass-card">""", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="
            background: #f8fafc;
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            border: 1px dashed #cbd5e1;
            font-size: 0.9rem;
            color: #64748b;
        ">
            📋 <strong>Total Questions:</strong> {num_questions} | <strong>Options:</strong> {", ".join(option_letters)}
        </div>
        """, unsafe_allow_html=True)

        # Create answer input with OMR-style radio buttons
        submitted_answers = []

        # Calculate questions per column
        questions_per_column = (num_questions + 1) // 2

        # Create 2 columns for better layout
        col1, col2 = st.columns(2)

        # First column - questions 1 to questions_per_column
        with col1:
            for i in range(questions_per_column):
                if i < num_questions:
                    answer = st.radio(
                        f"**Q{i+1}**",
                        options=option_letters,
                        horizontal=True,
                        index=None,
                        key=f"submit_answer_{i}",
                    )
                    submitted_answers.append(answer)

        # Second column - remaining questions
        with col2:
            for i in range(questions_per_column, num_questions):
                answer = st.radio(
                    f"**Q{i+1}**",
                    options=option_letters,
                    horizontal=True,
                    index=None,
                    key=f"submit_answer_{i}",
                )
                submitted_answers.append(answer)

        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("🚀 Submit Examination", use_container_width=True, key="submit_exam"):
            # Validate all answers are selected
            if None in submitted_answers:
                st.error("⚠️ Please answer all questions before submitting!")
                return

            # Submit the answers
            try:
                # Calculate score
                score = calculate_score(correct_answers, submitted_answers)
                
                # Save attempt to database
                success = db.save_attempt(
                    chapter_id, student_name, submitted_answers, 
                    score, len(correct_answers), attempt_count + 1
                )
                
                if success:
                    st.balloons()
                    st.markdown("""
                    <div style="
                        background: rgba(16, 185, 129, 0.1);
                        border: 1px solid rgba(16, 185, 129, 0.3);
                        border-radius: 12px;
                        padding: 1.5rem;
                        color: #065f46;
                        margin: 1.5rem 0;
                    ">
                        <strong style="color: #059669;">✅ Test submitted successfully!</strong><br>
                        View your performance and analysis below.
                    </div>
                    """, unsafe_allow_html=True)

                    # Display Results
                    st.markdown('<div style="margin-top: 2rem;"></div>',
                                unsafe_allow_html=True)
                    st.markdown('<h3 style="font-weight: 800; margin-bottom: 1.5rem;">📊 Performance Summary</h3>',
                                unsafe_allow_html=True)

                    m_col1, m_col2, m_col3 = st.columns(3)

                    score = attempt_result[3]
                    percentage = (score / num_questions) * 100

                    with m_col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{score}/{num_questions}</div>
                            <div class="metric-label">Total Score</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with m_col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{percentage:.1f}%</div>
                            <div class="metric-label">Percentage</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with m_col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{attempt_count + 1}</div>
                            <div class="metric-label">Attempt No.</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Answer comparison
                    st.markdown('<div style="margin-top: 2rem;"></div>',
                                unsafe_allow_html=True)
                    st.markdown("""<div class="glass-card">""", unsafe_allow_html=True)
                    st.markdown('<h3 style="font-weight: 700; margin-bottom: 1.5rem;">📋 Answer Comparison</h3>',
                                unsafe_allow_html=True)

                    comparison_data = []
                    for i in range(len(submitted_answers)):
                        is_correct = submitted_answers[i] == correct_answers[i]
                        status = "✅ Correct" if is_correct else "❌ Wrong"
                        comparison_data.append({
                            'Q.No': i + 1,
                            'Your Answer': submitted_answers[i],
                            'Correct Answer': correct_answers[i],
                            'Status': status,
                            'IsCorrect': is_correct
                        })

                    df_comparison = pd.DataFrame(comparison_data)
                    df_display = df_comparison.drop(columns=['IsCorrect'])

                    html_table = df_display.to_html(
                        classes='table table-hover',
                        index=False,
                        escape=False
                    )
                    html_table = html_table.replace(
                        '✅ Correct',
                        '<span class="badge bg-success">✅ Correct</span>')
                    html_table = html_table.replace(
                        '❌ Wrong',
                        '<span class="badge bg-danger">❌ Wrong</span>')

                    st.markdown(html_table, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error submitting exam: {str(e)}")


def view_results_page():
    """Page to view results chapter-wise"""
    db = st.session_state.db
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 3rem;
        color: white;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 40px rgba(8, 145, 178, 0.2);
    ">
        <div style="position: absolute; top: -10%; right: -5%; width: 300px; height: 300px; background: rgba(255,255,255,0.1); border-radius: 50%;"></div>
        <div style="position: relative; z-index: 1;">
            <span style="background: rgba(255,255,255,0.2); padding: 6px 16px; border-radius: 50px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;">📊 Result Analysis</span>
            <h2 style="color: white !important; font-size: 2.5rem; font-weight: 800; margin-top: 1rem; margin-bottom: 0.5rem;">View Results</h2>
            <p style="font-size: 1.1rem; opacity: 0.95; font-weight: 500; max-width: 600px; margin: 0;">Review your test attempts and detailed performance metrics.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Get all chapters
    chapters_df = db.get_all_chapters()

    if chapters_df.empty:
        st.markdown("""
        <div style="
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            color: #b91c1c;
        ">
            <strong>⚠️ No chapters available</strong>
        </div>
        """, unsafe_allow_html=True)
        return

    # Results Filter
    st.markdown("""<div class="glass-card">""", unsafe_allow_html=True)
    
    row_col1, row_col2, row_col3 = st.columns([1, 1.5, 2])

    with row_col1:
        chapter_name = st.selectbox(
            "📚 Select Chapter",
            options=chapters_df['chapter_name'].tolist(),
            key="results_chapter"
        )

    if not chapter_name:
        return

    # Fetch attempts
    attempts_df = db.get_student_attempts(chapter_name)

    if attempts_df.empty:
        with row_col2:
            st.info("No attempts found.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    with row_col2:
        attempt_index = st.selectbox(
            "👤 Select Student Attempt",
            options=range(len(attempts_df)),
            format_func=lambda x: f"{attempts_df.iloc[x]['student_name']} - Attempt #{attempts_df.iloc[x]['attempt_number']}",
            key="top_attempt_selection"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    if attempt_index is not None:
        selected_attempt = attempts_df.iloc[attempt_index]
        submitted_answers = json.loads(selected_attempt['submitted_answers'])

        # Get correct answers
        chapter = db.get_chapter_by_name(chapter_name)
        correct_answers = json.loads(chapter[4])

        # Display Answer Comparison
        st.markdown("""<div class="glass-card">""", unsafe_allow_html=True)
        ir_col1, ir_col2 = st.columns([0.5, 1])
        with ir_col1:
            st.markdown(
                '<p style="margin-top: 30px; font-weight: 600; font-size: 0.9rem;">Filter Status:</p>', unsafe_allow_html=True)
        with ir_col2:
            filter_option = st.radio(
                "Filter by Status",
                options=["All", "Correct", "Incorrect"],
                horizontal=True,
                key=f"filter_comparison_{attempt_index}",
                label_visibility="visible"  # Radio needs label for spacing usually
            )
        
        # Note: label_visibility="visible" but we hide the label text via CSS if needed,
        # or use a blank string if we want it super clean.
        # Let's try visible first to see alignment.

        # Move on to processing
        comparison_data = []
        for i in range(len(submitted_answers)):
            is_correct = submitted_answers[i] == correct_answers[i]
            status = "✅ Correct" if is_correct else "❌ Wrong"
            comparison_data.append({
                "Question": f"Q.{i + 1}",
                "Student Answer": submitted_answers[i],
                "Correct Answer": correct_answers[i],
                "Status": status,
                "IsCorrect": is_correct
            })

        df_comparison = pd.DataFrame(comparison_data)

        # Apply filter
        if filter_option == "Correct":
            df_filtered = df_comparison[df_comparison['IsCorrect'] == True].copy(
            )
        elif filter_option == "Incorrect":
            df_filtered = df_comparison[df_comparison['IsCorrect'] == False].copy(
            )
        else:
            df_filtered = df_comparison.copy()

        # Remove IsCorrect column for display
        df_display = df_filtered.drop(columns=['IsCorrect'])

        # Show count
        st.markdown(f"""
        <div class="alert alert-info mt-2 mb-3" role="alert">
            Showing <strong>{len(df_display)}</strong> of <strong>{len(df_comparison)}</strong> questions
        </div>
        """, unsafe_allow_html=True)

        # Apply Bootstrap table classes
        html_table = df_display.to_html(
            classes='table table-hover',
            index=False,
            escape=False
        )
        html_table = html_table.replace(
            '✅ Correct', '<span class="badge bg-success">Correct</span>')
        html_table = html_table.replace(
            '❌ Wrong', '<span class="badge bg-danger">Wrong</span>')

        st.markdown(html_table, unsafe_allow_html=True)

        # Export section
        st.markdown('<hr class="my-3">', unsafe_allow_html=True)
        st.markdown("""
        <div class="alert alert-info" role="alert">
            <strong>📥 Export Comparison Data</strong><br>
            Download the filtered answer comparison as an Excel file.
        </div>
        """, unsafe_allow_html=True)

        # Create Excel file for export
        excel_data = create_excel_download(
            student_name=selected_attempt['student_name'],
            chapter_name=chapter_name,
            score=selected_attempt['score'],
            total_questions=selected_attempt['total_questions'],
            percentage=(selected_attempt['score'] /
                        selected_attempt['total_questions'] * 100),
            attempt_number=selected_attempt['attempt_number'],
            submitted_answers=submitted_answers,
            correct_answers=correct_answers,
            submitted_at=selected_attempt['submitted_at']
        )

        # Create download button
        filename = f"{selected_attempt['student_name']}_{chapter_name}_Attempt{selected_attempt['attempt_number']}_Comparison.xlsx"

        st.download_button(
            label="📥 Download Excel Report",
            data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download complete exam report with answer comparison",
            use_container_width=True,
            type="secondary",
            key=f"download_comparison_{attempt_index}"
        )
    else:
        st.markdown("""
        <div class="alert alert-info" role="alert">
            No attempts found for the selected criteria.
        </div>
        """, unsafe_allow_html=True)


def analytics_page():
    """Page to show analytics and statistics"""
    db = st.session_state.db
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 3rem;
        color: white;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 40px rgba(5, 150, 105, 0.2);
    ">
        <div style="position: absolute; top: -10%; right: -5%; width: 300px; height: 300px; background: rgba(255,255,255,0.1); border-radius: 50%;"></div>
        <div style="position: relative; z-index: 1;">
            <span style="background: rgba(255,255,255,0.2); padding: 6px 16px; border-radius: 50px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;">📈 Analytics Dashboard</span>
            <h2 style="color: white !important; font-size: 2.5rem; font-weight: 800; margin-top: 1rem; margin-bottom: 0.5rem;">Performance Analytics</h2>
            <p style="font-size: 1.1rem; opacity: 0.95; font-weight: 500; max-width: 600px; margin: 0;">Comprehensive insights into test performance and student progress.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Get all chapters and attempts
    chapters_df = db.get_all_chapters()

    if chapters_df.empty:
        st.markdown("""
        <div style="
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            color: #b91c1c;
        ">
            <strong>⚠️ No data available</strong> - Create chapters and submit tests to see analytics.
        </div>
        """, unsafe_allow_html=True)
        return

    all_attempts_df = db.get_all_attempts()

    if all_attempts_df.empty:
        st.markdown("""
        <div style="
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            color: #1e40af;
        ">
            <strong>ℹ️ No attempts yet</strong> - Submit test attempts to generate analytics.
        </div>
        """, unsafe_allow_html=True)
        return

    # Overall statistics
    st.markdown('<h3 style="font-weight: 800; margin: 2rem 0 1.5rem 0;">📊 Overall Statistics</h3>',
                unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(chapters_df)}</div>
            <div class="metric-label">📚 Chapters</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(all_attempts_df)}</div>
            <div class="metric-label">✍️ Attempts</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        unique_students = all_attempts_df['student_name'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{unique_students}</div>
            <div class="metric-label">👥 Students</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        overall_avg = (
            all_attempts_df['score'] / all_attempts_df['total_questions'] * 100).mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{overall_avg:.1f}%</div>
            <div class="metric-label">📊 Avg Score</div>
        </div>
        """, unsafe_allow_html=True)

    # Chapter-wise performance
    st.markdown('<h3 style="font-weight: 800; margin: 3rem 0 1.5rem 0;">📚 Chapter-wise Performance</h3>',
                unsafe_allow_html=True)

    st.markdown("""<div class="glass-card">""", unsafe_allow_html=True)

    chapter_stats = all_attempts_df.groupby('chapter_name').agg({
        'id': 'count',
        'score': 'mean',
        'total_questions': 'first',
        'student_name': 'nunique'
    }).reset_index()

    chapter_stats.columns = ['Chapter', 'Total Attempts',
                             'Avg Score', 'Total Questions', 'Unique Students']
    chapter_stats['Avg Percentage'] = (
        chapter_stats['Avg Score'] / chapter_stats['Total Questions'] * 100).round(2)

    # Apply modern table styling
    st.markdown(chapter_stats.to_html(
        classes='table table-hover',
        index=False,
        escape=False
    ), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Top performers
    st.markdown('<h3 style="font-weight: 800; margin: 3rem 0 1.5rem 0;">🏆 Top Performers</h3>',
                unsafe_allow_html=True)

    st.markdown("""<div class="glass-card">""", unsafe_allow_html=True)

    # Student-wise performance
    st.markdown('<h3 class="fw-bold mt-4 mb-3">Top Performers</h3>',
                unsafe_allow_html=True)

    student_stats = all_attempts_df.groupby('student_name').agg({
        'id': 'count',
        'score': 'sum',
        'total_questions': 'sum'
    }).reset_index()

    student_stats.columns = [
        'Student', 'Total Attempts', 'Total Score', 'Total Questions']
    student_stats['Percentage'] = (
        student_stats['Total Score'] / student_stats['Total Questions'] * 100).round(2)
    student_stats = student_stats.sort_values(
        'Percentage', ascending=False).head(10)

    # Apply Bootstrap table classes with striped rows
    st.markdown(student_stats.to_html(
        classes='table table-striped table-hover',
        index=False,
        escape=False
    ), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
