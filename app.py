import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import json
from PIL import Image
import os

# Helper functions for options


def get_option_letters(num_options):
    """Get list of option letters based on number of options"""
    return [chr(65 + i) for i in range(num_options)]  # A, B, C, D, E, F

# Database setup


def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect('omr_data.db')
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
    conn.close()

# Database operations


def save_chapter(chapter_name, num_questions, num_options, correct_answers):
    """Save chapter configuration to database"""
    conn = sqlite3.connect('omr_data.db')
    c = conn.cursor()

    try:
        c.execute('''INSERT INTO chapters (chapter_name, num_questions, num_options, correct_answers)
                     VALUES (?, ?, ?, ?)''',
                  (chapter_name, num_questions, num_options, json.dumps(correct_answers)))
        conn.commit()
        return True, "Chapter saved successfully!"
    except sqlite3.IntegrityError:
        return False, "Chapter already exists!"
    finally:
        conn.close()


def get_all_chapters():
    """Get all chapters from database"""
    conn = sqlite3.connect('omr_data.db')
    df = pd.read_sql_query("SELECT * FROM chapters", conn)
    conn.close()
    return df


def get_chapter_by_name(chapter_name):
    """Get chapter details by name"""
    conn = sqlite3.connect('omr_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM chapters WHERE chapter_name = ?", (chapter_name,))
    result = c.fetchone()
    conn.close()
    return result


def get_attempt_count(chapter_id, student_name):
    """Get the number of attempts for a student on a specific chapter"""
    conn = sqlite3.connect('omr_data.db')
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) FROM attempts 
                 WHERE chapter_id = ? AND student_name = ?''',
              (chapter_id, student_name))
    count = c.fetchone()[0]
    conn.close()
    return count


def save_db_table_in_json():
    conn = sqlite3.connect('omr_data.db')
    df = pd.read_sql_query("SELECT * FROM attempts", conn)
    conn.close()
    # save df in json file
    df.to_json(
        f'attempts_data/attempts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', orient='records')


def save_attempt(chapter_id, student_name, submitted_answers, score, total_questions, attempt_number):
    """Save student attempt to database"""
    conn = sqlite3.connect('omr_data.db')
    c = conn.cursor()

    c.execute('''INSERT INTO attempts 
                 (chapter_id, student_name, submitted_answers, score, total_questions, attempt_number)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (chapter_id, student_name, json.dumps(submitted_answers), score, total_questions, attempt_number))

    conn.commit()
    conn.close()
    save_db_table_in_json()


def get_student_attempts(chapter_name, student_name=None):
    """Get all attempts for a chapter, optionally filtered by student"""
    conn = sqlite3.connect('omr_data.db')

    if student_name:
        query = '''SELECT a.*, c.chapter_name 
                   FROM attempts a
                   JOIN chapters c ON a.chapter_id = c.id
                   WHERE c.chapter_name = ? AND a.student_name = ?
                   ORDER BY a.submitted_at DESC'''
        df = pd.read_sql_query(
            query, conn, params=(chapter_name, student_name))
    else:
        query = '''SELECT a.*, c.chapter_name 
                   FROM attempts a
                   JOIN chapters c ON a.chapter_id = c.id
                   WHERE c.chapter_name = ?
                   ORDER BY a.submitted_at DESC'''
        df = pd.read_sql_query(query, conn, params=(chapter_name,))

    conn.close()
    return df


def calculate_score(correct_answers, submitted_answers):
    """Calculate score based on correct and submitted answers"""
    correct_count = 0
    for i, (correct, submitted) in enumerate(zip(correct_answers, submitted_answers)):
        if correct == submitted:
            correct_count += 1

    return correct_count

# Streamlit UI


def main():
    st.set_page_config(page_title="OMR Sheet Submission System",
                       page_icon="📝", layout="wide")

    # Custom CSS for Premium Look
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    /* Global Styles */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* Animation */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .main > div {
        animation: fadeInUp 0.6s ease-out;
    }

    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }

    /* Card/Sheet Styling */
    .omr-sheet-container {
        background-color: white;
        padding: 3rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        margin-top: 2rem;
    }

    /* OMR Radio Button Styling */
    .stRadio > label {
        font-weight: 600 !important;
        font-size: 1rem !important;
        color: #334155 !important;
        margin-bottom: 8px !important;
    }

    .stRadio > div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 15px !important;
        padding: 5px 0 !important;
    }

    .stRadio div[role="radiogroup"] > label {
        background-color: #f8fafc !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        padding: 0 !important;
        margin: 0 !important;
        font-weight: 700 !important;
        color: #475569 !important;
    }

    .stRadio div[role="radiogroup"] > label:hover {
        border-color: #2563eb !important;
        background-color: #eff6ff !important;
        transform: scale(1.1);
    }

    div[data-testid="stRadio"] label[data-checked="true"] {
        background-color: #1e293b !important;
        border-color: #1e293b !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        transform: scale(1.05);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
    }

    .stButton > button[kind="secondary"] {
        background-color: #f1f5f9 !important;
        color: #1e293b !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 15px rgba(37, 99, 235, 0.2) !important;
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        padding: 20px !important;
        border-radius: 16px;
    }

    /* Footer Styles */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: #64748b;
        text-align: center;
        padding: 10px;
        font-size: 0.8rem;
        border-top: 1px solid #e2e8f0;
        z-index: 99;
    }

    /* Tables */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }

    </style>
    <div class="footer">
        © 2026 OMR Sheet Submission System • Built with Streamlit Premium UI
    </div>
    """, unsafe_allow_html=True)

    # Initialize database
    init_db()

    # Sidebar Header
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="color: #2563eb; margin: 0; font-size: 2rem;">📝 OMR</h1>
        <p style="color: #64748b; font-size: 0.8rem;">Professional Scanning System</p>
    </div>
    <hr style="margin-top: 0; margin-bottom: 2rem;">
    """, unsafe_allow_html=True)

    st.title("📝 OMR Sheet Submission System")
    st.markdown("---")

    # Sidebar for navigation
    menu = st.sidebar.selectbox(
        "Navigation",
        ["Exam", "Create Chapter", "View Results", "Analytics"]
    )

    if menu == "Create Chapter":
        create_chapter_page()
    elif menu == "Exam":
        submit_omr_page()
    elif menu == "View Results":
        view_results_page()
    elif menu == "Analytics":
        analytics_page()


def create_chapter_page():
    """Page to create a new chapter with answer key"""
    st.header("📚 Create New Chapter")

    col1, col2 = st.columns(2)

    with col1:
        chapter_name = st.text_input(
            "Chapter Name", placeholder="e.g., Chapter 1: Introduction")
        num_questions = st.number_input(
            "Number of Questions", min_value=1, max_value=100, value=10)

    with col2:
        num_options = st.number_input(
            "Number of Options per Question", min_value=2, max_value=6, value=4)

    st.markdown("### Enter Correct Answers")
    option_letters = get_option_letters(num_options)
    st.info(
        f"Select the correct option ({', '.join(option_letters)}) for each question")

    # Create answer key input with OMR-style radio buttons
    correct_answers = []

    # Calculate questions per column
    questions_per_column = (num_questions + 1) // 2  # Ceiling division

    # Create 2 columns
    col1, col2 = st.columns(2)

    # First column - questions 1 to questions_per_column
    with col1:
        for i in range(questions_per_column):
            if i < num_questions:
                answer = st.radio(
                    f"Q{i+1}",
                    options=option_letters,
                    horizontal=True,
                    index=None,
                    key=f"answer_{i}"
                )
                correct_answers.append((i, answer))  # Store with index

    # Second column - remaining questions
    with col2:
        for i in range(questions_per_column, num_questions):
            answer = st.radio(
                f"Q{i+1}",
                options=option_letters,
                horizontal=True,
                index=None,
                key=f"answer_{i}"
            )
            correct_answers.append((i, answer))  # Store with index

    # Sort by index and extract just the answers
    correct_answers.sort(key=lambda x: x[0])
    correct_answers = [ans for idx, ans in correct_answers]

    if st.button("💾 Save Chapter", type="primary"):
        if not chapter_name:
            st.error("Please enter a chapter name!")
        elif None in correct_answers:
            st.error("⚠️ Please answer all questions before saving!")
        else:
            success, message = save_chapter(
                chapter_name, num_questions, num_options, correct_answers)
            if success:
                st.success(message)
            else:
                st.error(message)

    # Display existing chapters
    st.markdown("---")
    st.subheader("Existing Chapters")
    chapters_df = get_all_chapters()
    if not chapters_df.empty:
        display_df = chapters_df[['chapter_name',
                                  'num_questions', 'num_options', 'created_at']]
        st.dataframe(display_df, width='stretch', hide_index=True)
    else:
        st.info("No chapters created yet.")


def submit_omr_page():
    """Page to Exam"""
    st.header("✍️ Take a Test")

    # Get all chapters
    chapters_df = get_all_chapters()

    if chapters_df.empty:
        st.warning("No chapters available. Please create a chapter first!")
        return

    # Student information
    col1, col2 = st.columns(2)

    with col1:
        student_name = st.text_input("Student Name", value="Arin Khamrai")

    with col2:
        chapter_name = st.selectbox(
            "Select Chapter",
            options=chapters_df['chapter_name'].tolist()
        )

    if chapter_name:
        # Get chapter details
        chapter = get_chapter_by_name(chapter_name)
        chapter_id, _, num_questions, num_options, correct_answers_json, _ = chapter
        correct_answers = json.loads(correct_answers_json)

        # Display attempt count
        if student_name:
            attempt_count = get_attempt_count(chapter_id, student_name)
            st.info(
                f"This will be attempt #{attempt_count + 1} for {student_name}")

        option_letters = get_option_letters(num_options)
        st.markdown(
            f"### Answer Sheet ({num_questions} questions, options: {', '.join(option_letters)})")

        # Create answer input with OMR-style radio buttons
        submitted_answers = []

        # Calculate questions per column
        questions_per_column = (num_questions + 1) // 2

        # Create 2 columns
        col1, col2 = st.columns(2)

        # First column - questions 1 to questions_per_column
        with col1:
            for i in range(questions_per_column):
                if i < num_questions:
                    answer = st.radio(
                        f"Q{i+1}",
                        options=option_letters,
                        horizontal=True,
                        index=None,
                        key=f"submit_answer_{i}"
                    )
                    submitted_answers.append((i, answer))

        # Second column - remaining questions
        with col2:
            for i in range(questions_per_column, num_questions):
                answer = st.radio(
                    f"Q{i+1}",
                    options=option_letters,
                    horizontal=True,
                    index=None,
                    key=f"submit_answer_{i}"
                )
                submitted_answers.append((i, answer))

        # Sort by index and extract just the answers
        submitted_answers.sort(key=lambda x: x[0])
        submitted_answers = [ans for idx, ans in submitted_answers]

        if st.button("📤 Submit", type="primary"):
            if not student_name:
                st.error("Please enter your name!")
            elif None in submitted_answers:
                st.error("⚠️ Please answer all questions before submitting!")
            else:
                # Calculate score
                score = calculate_score(correct_answers, submitted_answers)
                percentage = (score / num_questions) * 100

                # Get attempt number
                attempt_number = get_attempt_count(
                    chapter_id, student_name) + 1

                # Save attempt
                save_attempt(chapter_id, student_name, submitted_answers,
                             score, num_questions, attempt_number)

                # Display results
                st.success("✅ OMR Sheet submitted successfully!")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Score", f"{score}/{num_questions}")
                with col2:
                    st.metric("Percentage", f"{percentage:.2f}%")
                with col3:
                    st.metric("Attempt Number", attempt_number)

                # Show answer comparison
                with st.expander("📊 View Answer Comparison"):
                    comparison_data = []
                    for i in range(num_questions):
                        comparison_data.append({
                            "Question": f"Q.{i+1}",
                            "Your Answer": submitted_answers[i],
                            "Correct Answer": correct_answers[i],
                            "Status": "✅" if submitted_answers[i] == correct_answers[i] else "❌"
                        })

                    st.dataframe(pd.DataFrame(comparison_data),
                                 width='stretch', hide_index=True)


def view_results_page():
    """Page to view results chapter-wise"""
    st.header("📊 View Results")

    # Get all chapters
    chapters_df = get_all_chapters()

    if chapters_df.empty:
        st.warning("No chapters available.")
        return

    col1, col2 = st.columns(2)

    with col1:
        chapter_name = st.selectbox(
            "Select Chapter",
            options=chapters_df['chapter_name'].tolist(),
            key="results_chapter"
        )

    with col2:
        student_name = st.text_input(
            "Filter by Student Name (optional)", placeholder="Leave empty for all students")

    if chapter_name:
        # Get attempts
        if student_name:
            attempts_df = get_student_attempts(chapter_name, student_name)
        else:
            attempts_df = get_student_attempts(chapter_name)

        if not attempts_df.empty:
            st.markdown(f"### Results for {chapter_name}")

            # Display summary statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Attempts", len(attempts_df))
            with col2:
                avg_score = attempts_df['score'].mean()
                avg_total = attempts_df['total_questions'].mean()
                st.metric("Average Score", f"{avg_score:.1f}/{avg_total:.0f}")
            with col3:
                avg_percentage = (
                    attempts_df['score'] / attempts_df['total_questions'] * 100).mean()
                st.metric("Average %", f"{avg_percentage:.2f}%")
            with col4:
                unique_students = attempts_df['student_name'].nunique()
                st.metric("Unique Students", unique_students)

            # Display attempts table
            st.markdown("### All Attempts")
            display_df = attempts_df[[
                'student_name', 'score', 'total_questions', 'attempt_number', 'submitted_at']].copy()
            display_df['percentage'] = (
                display_df['score'] / display_df['total_questions'] * 100).round(2)
            display_df = display_df.rename(columns={
                'student_name': 'Student',
                'score': 'Score',
                'total_questions': 'Total',
                'attempt_number': 'Attempt #',
                'submitted_at': 'Submitted At',
                'percentage': 'Percentage'
            })

            st.dataframe(display_df, width='stretch', hide_index=True)

            # Show detailed view for selected attempt
            st.markdown("### Detailed View")
            attempt_index = st.selectbox(
                "Select Attempt to View Details",
                options=range(len(attempts_df)),
                format_func=lambda x: f"{attempts_df.iloc[x]['student_name']} - Attempt #{attempts_df.iloc[x]['attempt_number']} - {attempts_df.iloc[x]['submitted_at']}"
            )

            if attempt_index is not None:
                selected_attempt = attempts_df.iloc[attempt_index]
                submitted_answers = json.loads(
                    selected_attempt['submitted_answers'])

                # Get correct answers
                chapter = get_chapter_by_name(chapter_name)
                correct_answers = json.loads(chapter[4])

                # Show comparison
                comparison_data = []
                for i in range(len(submitted_answers)):
                    comparison_data.append({
                        "Question": "Q."+str(i + 1),
                        "Student Answer": submitted_answers[i],
                        "Correct Answer": correct_answers[i],
                        "Status": "✅ Correct" if submitted_answers[i] == correct_answers[i] else "❌ Wrong"
                    })

                st.dataframe(pd.DataFrame(comparison_data),
                             width='stretch', hide_index=True)
        else:
            st.info("No attempts found for the selected criteria.")


def analytics_page():
    """Page to show analytics and statistics"""
    st.header("📈 Analytics Dashboard")

    # Get all chapters and attempts
    chapters_df = get_all_chapters()

    if chapters_df.empty:
        st.warning("No data available for analytics.")
        return

    conn = sqlite3.connect('omr_data.db')
    all_attempts_df = pd.read_sql_query('''
        SELECT a.*, c.chapter_name 
        FROM attempts a
        JOIN chapters c ON a.chapter_id = c.id
    ''', conn)
    conn.close()

    if all_attempts_df.empty:
        st.info("No attempts recorded yet.")
        return

    # Overall statistics
    st.markdown("### Overall Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Chapters", len(chapters_df))
    with col2:
        st.metric("Total Attempts", len(all_attempts_df))
    with col3:
        st.metric("Unique Students", all_attempts_df['student_name'].nunique())
    with col4:
        overall_avg = (
            all_attempts_df['score'] / all_attempts_df['total_questions'] * 100).mean()
        st.metric("Overall Avg %", f"{overall_avg:.2f}%")

    # Chapter-wise performance
    st.markdown("### Chapter-wise Performance")
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

    st.dataframe(chapter_stats, width='stretch', hide_index=True)

    # Student-wise performance
    st.markdown("### Top Performers")
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

    st.dataframe(student_stats, width='stretch', hide_index=True)


if __name__ == "__main__":
    main()
