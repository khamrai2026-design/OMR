import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import json
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

    # Premium UI/UX Design with Bootstrap & Custom CSS
    st.markdown("""
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    
    <style>
    /* ==================== GLOBAL STYLES ==================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* ==================== ANIMATIONS ==================== */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
    
    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }
    
    /* ==================== MAIN LAYOUT ==================== */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
        padding-bottom: 3rem;
    }
    
    .main > div {
        animation: fadeInUp 0.6s ease-out;
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* ==================== SIDEBAR ==================== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* Sidebar text */
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    /* Sidebar selectbox */
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
    }
    
    /* ==================== CARDS & CONTAINERS ==================== */
    .element-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.5);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .element-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.4);
    }
    
    /* ==================== TYPOGRAPHY ==================== */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 700 !important;
        color: #1e293b !important;
        letter-spacing: -0.5px;
    }
    
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    h2 {
        color: #334155 !important;
        font-size: 1.75rem !important;
    }
    
    h3 {
        color: #475569 !important;
        font-size: 1.5rem !important;
    }
    
    p {
        color: #64748b;
        line-height: 1.7;
    }
    
    /* ==================== OMR RADIO BUTTONS ==================== */
    .stRadio > label {
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        color: #1e293b !important;
        margin-bottom: 12px !important;
        display: flex !important;
        align-items: center !important;
    }
    
    .stRadio > div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 16px !important;
        padding: 10px 0 !important;
        flex-wrap: nowrap !important;
    }
    
    /* OMR Bubble Design */
    .stRadio div[role="radiogroup"] > label {
        background: linear-gradient(145deg, #ffffff, #f8fafc) !important;
        border: 3px solid #cbd5e1 !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        padding: 0 !important;
        margin: 0 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        color: #475569 !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    /* Hover effect */
    .stRadio div[role="radiogroup"] > label:hover {
        border-color: #667eea !important;
        background: linear-gradient(145deg, #eff6ff, #dbeafe) !important;
        transform: scale(1.15) rotate(5deg);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
    }
    
    /* Selected state */
    .stRadio div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-color: #667eea !important;
        color: white !important;
        transform: scale(1.1);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.5);
        animation: pulse 0.5s ease-in-out;
    }
    
    /* Hide default radio circle */
    .stRadio div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    
    /* ==================== BUTTONS ==================== */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* ==================== METRICS ==================== */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        padding: 1.5rem !important;
        border-radius: 16px;
        border: 2px solid transparent;
        background-clip: padding-box;
        position: relative;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 16px;
        padding: 2px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        z-index: -1;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
    }
    
    div[data-testid="stMetric"] label {
        color: #64748b !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #1e293b !important;
        font-weight: 800 !important;
        font-size: 2rem !important;
    }
    
    /* ==================== INPUT FIELDS ==================== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        background-color: white !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        outline: none !important;
    }
    
    /* ==================== DATAFRAMES ==================== */
    .stDataFrame {
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    .stDataFrame table {
        font-size: 0.95rem !important;
    }
    
    .stDataFrame thead tr th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.875rem !important;
    }
    
    .stDataFrame tbody tr {
        transition: all 0.2s ease;
    }
    
    .stDataFrame tbody tr:hover {
        background-color: #f8fafc !important;
        transform: scale(1.01);
    }
    
    /* ==================== EXPANDER ==================== */
    .streamlit-expanderHeader {
        background: linear-gradient(145deg, #f8fafc, #ffffff) !important;
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #667eea !important;
        background: linear-gradient(145deg, #eff6ff, #f8fafc) !important;
    }
    
    /* ==================== INFO/WARNING/SUCCESS BOXES ==================== */
    .stAlert {
        border-radius: 12px !important;
        border-left: 4px solid !important;
        padding: 1rem 1.5rem !important;
        backdrop-filter: blur(10px);
    }
    
    .stSuccess {
        background: linear-gradient(145deg, #ecfdf5, #d1fae5) !important;
        border-left-color: #10b981 !important;
    }
    
    .stWarning {
        background: linear-gradient(145deg, #fffbeb, #fef3c7) !important;
        border-left-color: #f59e0b !important;
    }
    
    .stError {
        background: linear-gradient(145deg, #fef2f2, #fee2e2) !important;
        border-left-color: #ef4444 !important;
    }
    
    .stInfo {
        background: linear-gradient(145deg, #eff6ff, #dbeafe) !important;
        border-left-color: #3b82f6 !important;
    }
    
    /* ==================== SCROLLBAR ==================== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        border: 2px solid #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* ==================== FOOTER ==================== */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        color: #64748b;
        text-align: center;
        padding: 0.75rem;
        font-size: 0.875rem;
        border-top: 1px solid rgba(226, 232, 240, 0.8);
        z-index: 999;
        box-shadow: 0 -5px 20px rgba(0, 0, 0, 0.05);
    }
    
    /* ==================== RESPONSIVE ==================== */
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem !important;
        }
        
        .stRadio div[role="radiogroup"] > label {
            width: 40px !important;
            height: 40px !important;
            font-size: 0.9rem !important;
        }
    }
    </style>
    
    <!-- Footer -->
    <div class="footer">
        <i class="bi bi-shield-check"></i> © 2026 OMR Professional System • Powered by Streamlit & Bootstrap 5
    </div>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
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
        ["Exam",  "View Results", "Analytics"]
    )

    if menu == "Exam":
        submit_omr_page()
    elif menu == "View Results":
        view_results_page()
    elif menu == "Analytics":
        analytics_page()


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
