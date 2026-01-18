
import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import json
import os
from io import BytesIO

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
    # save_db_table_in_json()


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

    # Bootstrap 5 CSS
    st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
    /* Custom styles */
    .card {
        margin-bottom: 1.5rem;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .card-header {
        background-color: #f8f9fa;
        font-weight: 600;
        padding: 0.75rem 1.25rem;
    }
    .btn-primary {
        background-color: #0d6efd;
        border-color: #0d6efd;
    }
    .btn-primary:hover {
        background-color: #0b5ed7;
        border-color: #0a58ca;
    }
    .btn-success {
        background-color: #198754;
        border-color: #198754;
    }
    .btn-success:hover {
        background-color: #157347;
        border-color: #146c43;
    }
    .table {
        width: 100%;
        margin-bottom: 1rem;
        background-color: transparent;
    }
    .table th {
        border-top: none;
        font-weight: 600;
        color: #495057;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 0.5rem;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #dee2e6;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0d6efd;
    }
    .metric-label {
        font-size: 0.875rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stSelectbox, .stTextInput, .stRadio {
        margin-bottom: 1rem;
    }
    /* Custom radio button styling */
    .stRadio > div[data-baseweb="radio"] {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }
    .stRadio > div[data-baseweb="radio"] > div {
        margin-right: 10px;
    }
    .stRadio label {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .stRadio label:hover {
        background-color: #e9ecef;
        border-color: #adb5bd;
    }
    .stRadio input[type="radio"]:checked + label {
        background-color: #0d6efd;
        color: white;
        border-color: #0d6efd;
    }
    /* Button container styling */
    .button-container {
        display: flex;
        gap: 10px;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .download-btn {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize database
    init_db()

    # Sidebar Header with Bootstrap styling
    st.sidebar.markdown("""
    <div class="text-center py-4">
        <h1 class="text-primary mb-2" style="font-size: 2rem;">📝 OMR</h1>
        <p class="text-muted mb-0" style="font-size: 0.9rem;">Professional Scanning System</p>
    </div>
    <hr class="my-3">
    """, unsafe_allow_html=True)

    # Main title with Bootstrap classes
    st.markdown("""
    <div class="container-fluid py-4">
        <h1 class="display-6 fw-bold text-primary">📝 OMR Sheet Submission System</h1>
        <p class="lead text-muted">Submit and evaluate OMR sheets with professional analytics</p>
    </div>
    <hr class="mb-4">
    """, unsafe_allow_html=True)

    # Sidebar for navigation with Bootstrap styling
    menu = st.sidebar.selectbox(
        "Navigation",
        ["Exam", "View Results", "Analytics"],
        key="main_nav"
    )

    # Add some spacing in sidebar
    st.sidebar.markdown('<div class="mt-4"></div>', unsafe_allow_html=True)

    if menu == "Exam":
        submit_omr_page()
    elif menu == "View Results":
        view_results_page()
    elif menu == "Analytics":
        analytics_page()


def submit_omr_page():
    """Page to Exam"""
    st.markdown('<h2 class="fw-bold mb-4">✍️ Take a Test</h2>',
                unsafe_allow_html=True)

    # Get all chapters
    chapters_df = get_all_chapters()

    if chapters_df.empty:
        st.markdown("""
        <div class="alert alert-warning" role="alert">
            No chapters available. Please create a chapter first!
        </div>
        """, unsafe_allow_html=True)
        return

    # Card container for student info
    st.markdown('<div class="card mb-4">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">Student Information</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="card-body">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        student_name = st.text_input("Student Name", value="Arin Khamrai",
                                     help="Enter your full name")

    with col2:
        chapter_name = st.selectbox(
            "Select Chapter",
            options=chapters_df['chapter_name'].tolist(),
            help="Choose the chapter for the test"
        )

    st.markdown('</div></div>', unsafe_allow_html=True)

    if chapter_name:
        # Get chapter details
        chapter = get_chapter_by_name(chapter_name)
        chapter_id, _, num_questions, num_options, correct_answers_json, _ = chapter
        correct_answers = json.loads(correct_answers_json)

        # Display attempt count
        if student_name:
            attempt_count = get_attempt_count(chapter_id, student_name)
            st.markdown(f"""
            <div class="alert alert-info" role="alert">
                This will be attempt <strong>#{attempt_count + 1}</strong> for <strong>{student_name}</strong>
            </div>
            """, unsafe_allow_html=True)

        option_letters = get_option_letters(num_options)

        # Card container for answer sheet
        st.markdown('<div class="card mb-4">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="card-header">Answer Sheet ({num_questions} questions, options: {", ".join(option_letters)})</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-body">', unsafe_allow_html=True)

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
                        key=f"submit_answer_{i}",
                        label_visibility="visible"
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
                    key=f"submit_answer_{i}",
                    label_visibility="visible"
                )
                submitted_answers.append((i, answer))

        st.markdown('</div></div>', unsafe_allow_html=True)

        # Sort by index and extract just the answers
        submitted_answers.sort(key=lambda x: x[0])
        submitted_answers_list = [ans for idx, ans in submitted_answers]

        # Submit button with Bootstrap styling
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📤 Submit Test", type="primary", use_container_width=True):
                if not student_name:
                    st.markdown("""
                    <div class="alert alert-danger" role="alert">
                        Please enter your name!
                    </div>
                    """, unsafe_allow_html=True)
                elif None in submitted_answers_list:
                    st.markdown("""
                    <div class="alert alert-danger" role="alert">
                        ⚠️ Please answer all questions before submitting!
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Calculate score
                    score = calculate_score(
                        correct_answers, submitted_answers_list)
                    percentage = (score / num_questions) * 100

                    # Get attempt number
                    attempt_number = get_attempt_count(
                        chapter_id, student_name) + 1

                    # Save attempt
                    save_attempt(chapter_id, student_name, submitted_answers_list,
                                 score, num_questions, attempt_number)

                    # Display success message
                    st.markdown("""
                    <div class="alert alert-success" role="alert">
                        ✅ OMR Sheet submitted successfully!
                    </div>
                    """, unsafe_allow_html=True)

                    # Results card
                    st.markdown('<div class="card mb-4">',
                                unsafe_allow_html=True)
                    st.markdown(
                        '<div class="card-header">Test Results</div>', unsafe_allow_html=True)
                    st.markdown('<div class="card-body">',
                                unsafe_allow_html=True)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{score}/{num_questions}</div>
                            <div class="metric-label">Score</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{percentage:.2f}%</div>
                            <div class="metric-label">Percentage</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{attempt_number}</div>
                            <div class="metric-label">Attempt #</div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown('</div></div>', unsafe_allow_html=True)

                    # Show answer comparison in accordion
                    st.markdown('<div class="card mb-4">',
                                unsafe_allow_html=True)
                    st.markdown(
                        '<div class="card-header">📊 Answer Comparison</div>', unsafe_allow_html=True)
                    st.markdown('<div class="card-body">',
                                unsafe_allow_html=True)

                    # Create comparison data
                    comparison_data = []
                    for i in range(num_questions):
                        is_correct = submitted_answers_list[i] == correct_answers[i]
                        status_icon = "✅" if is_correct else "❌"
                        comparison_data.append({
                            "Question": f"Q.{i+1}",
                            "Your Answer": submitted_answers_list[i],
                            "Correct Answer": correct_answers[i],
                            "Status": status_icon,
                            "IsCorrect": is_correct  # For filtering
                        })

                    df_comparison = pd.DataFrame(comparison_data)

                    # Add filter options
                    filter_option = st.radio(
                        "Filter by Status:",
                        options=["All", "Correct", "Incorrect"],
                        horizontal=True,
                        key="filter_submit_comparison"
                    )

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
                    st.markdown(df_display.to_html(
                        classes='table table-hover table-bordered',
                        index=False,
                        escape=False
                    ), unsafe_allow_html=True)

                    st.markdown('</div></div>', unsafe_allow_html=True)

                    # ========== Download Excel Button ==========
                    st.markdown('<div class="card mb-4">',
                                unsafe_allow_html=True)
                    st.markdown(
                        '<div class="card-header">📥 Download Report</div>', unsafe_allow_html=True)
                    st.markdown('<div class="card-body">',
                                unsafe_allow_html=True)

                    st.markdown("""
                    <div class="alert alert-info" role="alert">
                        <strong>📋 Download Complete Exam Report</strong><br>
                        Get a detailed Excel report with all exam details, answer comparison, and performance analysis.
                    </div>
                    """, unsafe_allow_html=True)

                    # Create Excel file for download
                    excel_data = create_excel_download(
                        student_name=student_name,
                        chapter_name=chapter_name,
                        score=score,
                        total_questions=num_questions,
                        percentage=percentage,
                        attempt_number=attempt_number,
                        submitted_answers=submitted_answers_list,
                        correct_answers=correct_answers,
                        submitted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )

                    # Create download button
                    filename = f"{student_name}_{chapter_name}_Attempt{attempt_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

                    st.download_button(
                        label="📥 Download Excel Report",
                        data=excel_data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        help="Click to download complete exam report in Excel format",
                        use_container_width=True,
                        type="secondary"
                    )

                    st.markdown("""
                    <div class="mt-3">
                        <small class="text-muted">
                            <strong>Report includes:</strong><br>
                            1. Exam Summary - Basic information and scores<br>
                            2. Answer Comparison - Question-by-question analysis<br>
                            3. Performance Analysis - Detailed metrics and statistics<br>
                            4. Question Details - Complete breakdown with feedback
                        </small>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown('</div></div>', unsafe_allow_html=True)


def view_results_page():
    """Page to view results chapter-wise"""
    st.markdown('<h2 class="fw-bold mb-4">📊 View Results</h2>',
                unsafe_allow_html=True)

    # Get all chapters
    chapters_df = get_all_chapters()

    if chapters_df.empty:
        st.markdown("""
        <div class="alert alert-warning" role="alert">
            No chapters available.
        </div>
        """, unsafe_allow_html=True)
        return

    # Filter card
    st.markdown('<div class="card mb-4">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">Filter Options</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="card-body">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        chapter_name = st.selectbox(
            "Select Chapter",
            options=chapters_df['chapter_name'].tolist(),
            key="results_chapter"
        )

    with col2:
        student_name = st.text_input(
            "Filter by Student Name (optional)",
            placeholder="Leave empty for all students",
            help="Enter student name to filter results"
        )

    st.markdown('</div></div>', unsafe_allow_html=True)

    if chapter_name:
        # Get attempts
        if student_name:
            attempts_df = get_student_attempts(chapter_name, student_name)
        else:
            attempts_df = get_student_attempts(chapter_name)

        if not attempts_df.empty:
            st.markdown(
                f'<h3 class="fw-bold mb-3">Results for {chapter_name}</h3>', unsafe_allow_html=True)

            # Display summary statistics with Bootstrap cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(attempts_df)}</div>
                    <div class="metric-label">Total Attempts</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                avg_score = attempts_df['score'].mean()
                avg_total = attempts_df['total_questions'].mean()
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{avg_score:.1f}/{avg_total:.0f}</div>
                    <div class="metric-label">Average Score</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                avg_percentage = (
                    attempts_df['score'] / attempts_df['total_questions'] * 100).mean()
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{avg_percentage:.2f}%</div>
                    <div class="metric-label">Average %</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                unique_students = attempts_df['student_name'].nunique()
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{unique_students}</div>
                    <div class="metric-label">Unique Students</div>
                </div>
                """, unsafe_allow_html=True)

            # Display attempts table
            st.markdown(
                '<h4 class="fw-bold mt-4 mb-3">All Attempts</h4>', unsafe_allow_html=True)
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

            # Apply Bootstrap table classes
            st.markdown(display_df.to_html(
                classes='table table-striped table-hover',
                index=False,
                escape=False
            ), unsafe_allow_html=True)

            # Show detailed view for selected attempt
            st.markdown(
                '<h4 class="fw-bold mt-4 mb-3">Detailed View</h4>', unsafe_allow_html=True)

            # Card for attempt selection
            st.markdown('<div class="card mb-4">', unsafe_allow_html=True)
            st.markdown(
                '<div class="card-header">Select Attempt to View Details</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-body">', unsafe_allow_html=True)

            attempt_index = st.selectbox(
                "Select Attempt",
                options=range(len(attempts_df)),
                format_func=lambda x: f"{attempts_df.iloc[x]['student_name']} - Attempt #{attempts_df.iloc[x]['attempt_number']} - {attempts_df.iloc[x]['submitted_at']}",
                label_visibility="collapsed"
            )

            st.markdown('</div></div>', unsafe_allow_html=True)

            if attempt_index is not None:
                selected_attempt = attempts_df.iloc[attempt_index]
                submitted_answers = json.loads(
                    selected_attempt['submitted_answers'])

                # Get correct answers
                chapter = get_chapter_by_name(chapter_name)
                correct_answers = json.loads(chapter[4])

                # Show comparison in a table
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(
                    '<div class="card-header">Answer Comparison</div>', unsafe_allow_html=True)
                st.markdown('<div class="card-body">', unsafe_allow_html=True)

                # Create comparison data
                comparison_data = []
                for i in range(len(submitted_answers)):
                    is_correct = submitted_answers[i] == correct_answers[i]
                    status = "✅ Correct" if is_correct else "❌ Wrong"
                    comparison_data.append({
                        "Question": f"Q.{i + 1}",
                        "Student Answer": submitted_answers[i],
                        "Correct Answer": correct_answers[i],
                        "Status": status,
                        "IsCorrect": is_correct  # For filtering
                    })

                df_comparison = pd.DataFrame(comparison_data)

                # Add filter options
                col_filter, col_export = st.columns([2, 1])
                with col_filter:
                    filter_option = st.radio(
                        "Filter by Status:",
                        options=["All", "Correct", "Incorrect"],
                        horizontal=True,
                        key=f"filter_comparison_{attempt_index}"
                    )

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

                # Apply Bootstrap table classes with conditional formatting
                html_table = df_display.to_html(
                    classes='table table-hover',
                    index=False,
                    escape=False
                )
                # Add Bootstrap classes to table cells based on status
                html_table = html_table.replace(
                    '✅ Correct', '<span class="badge bg-success">Correct</span>')
                html_table = html_table.replace(
                    '❌ Wrong', '<span class="badge bg-danger">Wrong</span>')

                st.markdown(html_table, unsafe_allow_html=True)

                # Export functionality
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
                    percentage=(
                        selected_attempt['score'] / selected_attempt['total_questions'] * 100),
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

                st.markdown('</div></div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert alert-info" role="alert">
                No attempts found for the selected criteria.
            </div>
            """, unsafe_allow_html=True)


def analytics_page():
    """Page to show analytics and statistics"""
    st.markdown('<h2 class="fw-bold mb-4">📈 Analytics Dashboard</h2>',
                unsafe_allow_html=True)

    # Get all chapters and attempts
    chapters_df = get_all_chapters()

    if chapters_df.empty:
        st.markdown("""
        <div class="alert alert-warning" role="alert">
            No data available for analytics.
        </div>
        """, unsafe_allow_html=True)
        return

    conn = sqlite3.connect('omr_data.db')
    all_attempts_df = pd.read_sql_query('''
        SELECT a.*, c.chapter_name 
        FROM attempts a
        JOIN chapters c ON a.chapter_id = c.id
    ''', conn)
    conn.close()

    if all_attempts_df.empty:
        st.markdown("""
        <div class="alert alert-info" role="alert">
            No attempts recorded yet.
        </div>
        """, unsafe_allow_html=True)
        return

    # Overall statistics
    st.markdown('<h3 class="fw-bold mb-3">Overall Statistics</h3>',
                unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(chapters_df)}</div>
            <div class="metric-label">Total Chapters</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(all_attempts_df)}</div>
            <div class="metric-label">Total Attempts</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        unique_students = all_attempts_df['student_name'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{unique_students}</div>
            <div class="metric-label">Unique Students</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        overall_avg = (
            all_attempts_df['score'] / all_attempts_df['total_questions'] * 100).mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{overall_avg:.2f}%</div>
            <div class="metric-label">Overall Avg %</div>
        </div>
        """, unsafe_allow_html=True)

    # Chapter-wise performance
    st.markdown('<h3 class="fw-bold mt-4 mb-3">Chapter-wise Performance</h3>',
                unsafe_allow_html=True)

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

    # Apply Bootstrap table classes
    st.markdown(chapter_stats.to_html(
        classes='table table-striped table-hover',
        index=False,
        escape=False
    ), unsafe_allow_html=True)

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
