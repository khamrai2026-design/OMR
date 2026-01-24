"""
Modern OMR Digital Suite - Flask Web Application
A sleek, modern web-based OMR sheet evaluation system
"""
from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
import sqlite3
import json
import os
from io import BytesIO
from werkzeug.serving import run_simple

try:
    from utils.excel_exporter import ExcelExporter
except ImportError:
    ExcelExporter = None

app = Flask(__name__, template_folder='templates', static_folder='static')

# Database setup
DATABASE = 'omr_data.db'


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Create subjects table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS subjects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  subject_name TEXT UNIQUE NOT NULL,
                  description TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Create chapters table with subject_id
    c.execute('''CREATE TABLE IF NOT EXISTS chapters
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  subject_id INTEGER NOT NULL DEFAULT 1,
                  chapter_name TEXT UNIQUE NOT NULL,
                  num_questions INTEGER NOT NULL,
                  num_options INTEGER NOT NULL,
                  correct_answers TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (subject_id) REFERENCES subjects(id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS attempts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  chapter_id INTEGER NOT NULL,
                  student_name TEXT NOT NULL,
                  submitted_answers TEXT NOT NULL,
                  score REAL NOT NULL,
                  total_questions INTEGER NOT NULL,
                  attempt_number INTEGER NOT NULL,
                  time_taken INTEGER DEFAULT 0,
                  start_time TIMESTAMP,
                  end_time TIMESTAMP,
                  submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (chapter_id) REFERENCES chapters(id))''')

    # Migrations
    # 1. Add subject_id to chapters if missing
    try:
        c.execute('SELECT subject_id FROM chapters LIMIT 1')
    except sqlite3.OperationalError:
        c.execute(
            'ALTER TABLE chapters ADD COLUMN subject_id INTEGER NOT NULL DEFAULT 1')

    # 2. Add time_taken, start_time, end_time columns to attempts if missing
    try:
        c.execute('SELECT time_taken FROM attempts LIMIT 1')
    except sqlite3.OperationalError:
        c.execute('ALTER TABLE attempts ADD COLUMN time_taken INTEGER DEFAULT 0')

    try:
        c.execute('SELECT start_time FROM attempts LIMIT 1')
    except sqlite3.OperationalError:
        c.execute('ALTER TABLE attempts ADD COLUMN start_time TIMESTAMP')

    try:
        c.execute('SELECT end_time FROM attempts LIMIT 1')
    except sqlite3.OperationalError:
        c.execute('ALTER TABLE attempts ADD COLUMN end_time TIMESTAMP')

    conn.commit()
    conn.close()

# API Routes


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """Get all subjects"""
    conn = get_db()
    subjects = conn.execute(
        'SELECT * FROM subjects ORDER BY subject_name').fetchall()
    conn.close()
    return jsonify([dict(s) for s in subjects])


@app.route('/api/chapters', methods=['GET'])
def get_chapters():
    """Get chapters, optionally filtered by subject_id"""
    subject_id = request.args.get('subject_id')
    conn = get_db()

    if subject_id:
        chapters = conn.execute('SELECT * FROM chapters WHERE subject_id = ? ORDER BY created_at DESC',
                                (int(subject_id),)).fetchall()
    else:
        chapters = conn.execute(
            'SELECT * FROM chapters ORDER BY created_at DESC').fetchall()

    conn.close()
    return jsonify([dict(ch) for ch in chapters])


@app.route('/api/chapter/<int:chapter_id>', methods=['GET'])
def get_chapter(chapter_id):
    """Get chapter details"""
    conn = get_db()
    chapter = conn.execute(
        'SELECT * FROM chapters WHERE id = ?', (chapter_id,)).fetchone()
    conn.close()
    return jsonify(dict(chapter) if chapter else {})


@app.route('/api/submit-exam', methods=['POST'])
def submit_exam():
    """Submit exam answers"""
    data = request.json
    student_name = data.get('student_name')
    chapter_id = data.get('chapter_id')
    submitted_answers = data.get('submitted_answers')
    time_taken = data.get('time_taken', 0)  # Time in seconds
    start_time = data.get('start_time')  # ISO format datetime
    end_time = data.get('end_time')      # ISO format datetime

    conn = get_db()

    # Get chapter details
    chapter = conn.execute(
        'SELECT * FROM chapters WHERE id = ?', (chapter_id,)).fetchone()
    if not chapter:
        return jsonify({'success': False, 'message': 'Chapter not found'}), 404

    correct_answers = json.loads(chapter['correct_answers'])

    # Calculate score
    score = sum(1 for i, ans in enumerate(
        submitted_answers) if ans == correct_answers[i])

    # Get attempt number
    attempt = conn.execute(
        'SELECT MAX(attempt_number) as max_attempt FROM attempts WHERE chapter_id = ? AND student_name = ?',
        (chapter_id, student_name)
    ).fetchone()
    attempt_number = (attempt['max_attempt'] or 0) + 1

    # Save attempt with start_time and end_time
    conn.execute(
        '''INSERT INTO attempts (chapter_id, student_name, submitted_answers, score, total_questions, attempt_number, time_taken, start_time, end_time)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (chapter_id, student_name, json.dumps(submitted_answers), score, len(
            correct_answers), attempt_number, time_taken, start_time, end_time)
    )
    conn.commit()
    conn.close()

    # Calculate percentage and grade
    percentage = (score / len(correct_answers)) * 100
    grade = get_grade(percentage)
    passed = percentage >= 50

    return jsonify({
        'success': True,
        'score': score,
        'total': len(correct_answers),
        'percentage': percentage,
        'grade': grade,
        'passed': passed,
        'time_taken': time_taken,
        'attempt_number': attempt_number,
        'correct_answers': correct_answers
    })


def get_grade(percentage):
    """Calculate grade based on percentage"""
    if percentage >= 90:
        return 'A'
    elif percentage >= 80:
        return 'B'
    elif percentage >= 70:
        return 'C'
    elif percentage >= 60:
        return 'D'
    elif percentage >= 50:
        return 'E'
    else:
        return 'F'


@app.route('/api/results/<chapter_name>', methods=['GET'])
def get_results(chapter_name):
    """Get results for a chapter"""
    conn = get_db()

    # Get attempts
    attempts = conn.execute('''
        SELECT a.*, c.chapter_name, c.correct_answers
        FROM attempts a
        JOIN chapters c ON a.chapter_id = c.id
        WHERE c.chapter_name = ?
        ORDER BY a.submitted_at DESC
    ''', (chapter_name,)).fetchall()

    result_list = []
    for attempt in attempts:
        attempt_dict = dict(attempt)
        result_list.append(attempt_dict)

    conn.close()

    return jsonify(result_list)


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data"""
    conn = get_db()
    student_filter = request.args.get('student', None)
    subject_id_filter = request.args.get('subject_id', None)
    days = request.args.get('days', None)

    # Build WHERE clause and parameters for filters
    where_clauses = []
    params = []

    if student_filter:
        where_clauses.append("a.student_name = ?")
        params.append(student_filter)
    if subject_id_filter and subject_id_filter.isdigit():
        where_clauses.append("c.subject_id = ?")
        params.append(int(subject_id_filter))
    if days and days.isdigit():
        where_clauses.append(
            "a.submitted_at >= date('now', '-' || ? || ' days')")
        params.append(days)

    where_clause = "WHERE " + \
        " AND ".join(where_clauses) if where_clauses else ""

    # Overall stats
    chapters_query = 'SELECT COUNT(*) as count FROM chapters'
    chapters_params = []
    if subject_id_filter and subject_id_filter.isdigit():
        chapters_query += ' WHERE subject_id = ?'
        chapters_params.append(int(subject_id_filter))

    chapters_count = conn.execute(
        chapters_query, chapters_params).fetchone()['count']

    attempts_query = f'''
        SELECT COUNT(*) as count FROM attempts a
        JOIN chapters c ON a.chapter_id = c.id
        {where_clause}
    '''
    attempts_count = conn.execute(attempts_query, params).fetchone()['count']

    # Average score
    avg_query = f'''
        SELECT AVG(CAST(a.score as FLOAT) / a.total_questions * 100) as avg_percentage,
               MAX(CAST(a.score as FLOAT) / a.total_questions * 100) as best_score,
               AVG(CAST(a.score as FLOAT) / a.total_questions) as avg_accuracy
        FROM attempts a
        JOIN chapters c ON a.chapter_id = c.id
        {where_clause}
    '''
    avg_result = conn.execute(avg_query, params).fetchone()
    avg_percentage = avg_result['avg_percentage'] or 0
    best_score = avg_result['best_score'] or 0
    avg_accuracy = (avg_result['avg_accuracy'] or 0) * 100

    # Best score points
    best_score_query = f'''
        SELECT MAX(a.score) as max_score FROM attempts a
        JOIN chapters c ON a.chapter_id = c.id
        {where_clause}
    '''
    best_score_points = conn.execute(best_score_query, params).fetchone()[
        'max_score'] or 0

    # Chapter-wise stats (with LEFT JOIN to show all chapters in subject)
    join_filters = []
    join_params = []
    if student_filter:
        join_filters.append("a.student_name = ?")
        join_params.append(student_filter)
    if days and days.isdigit():
        join_filters.append(
            "a.submitted_at >= date('now', '-' || ? || ' days')")
        join_params.append(days)

    join_clause = "AND " + " AND ".join(join_filters) if join_filters else ""

    chapter_where = ""
    chapter_params = []
    if subject_id_filter and subject_id_filter.isdigit():
        chapter_where = "WHERE c.subject_id = ?"
        chapter_params.append(int(subject_id_filter))

    chapter_stats_query = f'''
        SELECT c.id, c.chapter_name, COUNT(a.id) as total_attempts, 
               MAX(CAST(a.score as FLOAT)) as best_score,
               AVG(CAST(a.score as FLOAT) / a.total_questions * 100) as avg_percentage,
               AVG(CAST(a.score as FLOAT) / a.total_questions) as avg_accuracy
        FROM chapters c
        LEFT JOIN attempts a ON c.id = a.chapter_id {join_clause}
        {chapter_where}
        GROUP BY c.id
        ORDER BY total_attempts DESC
    '''
    chapter_stats_raw = conn.execute(
        chapter_stats_query, join_params + chapter_params).fetchall()

    chapter_stats = []
    for stat in chapter_stats_raw:
        chapter_stats.append({
            'chapter_name': stat['chapter_name'],
            'total_attempts': stat['total_attempts'] or 0,
            'best_score': stat['best_score'] or 0,
            'avg_percentage': stat['avg_percentage'] or 0,
            'avg_accuracy': (stat['avg_accuracy'] or 0) * 100
        })

    # All attempts for charts
    all_attempts_query = f'''
        SELECT a.id, a.student_name, a.attempt_number, c.chapter_name, c.id as chapter_id,
               a.score, a.total_questions, COALESCE(a.time_taken, 0) as time_taken, a.submitted_at
        FROM attempts a
        JOIN chapters c ON a.chapter_id = c.id
        {where_clause}
        ORDER BY a.submitted_at DESC
    '''
    all_attempts = conn.execute(all_attempts_query, params).fetchall()

    conn.close()

    return jsonify({
        'total_attempts': attempts_count,
        'avg_score': round(avg_percentage, 2),
        'best_score': best_score_points,
        'avg_accuracy': round(avg_accuracy, 2),
        'chapter_stats': chapter_stats,
        'all_attempts': [dict(attempt) for attempt in all_attempts]
    })


@app.route('/api/export/exam', methods=['POST'])
def export_exam():
    """Export exam result as Excel"""
    if not ExcelExporter:
        return jsonify({'success': False, 'message': 'Excel export not available'}), 400

    data = request.json
    student_name = data.get('student_name')
    chapter_name = data.get('chapter_name')
    score = data.get('score')
    total_questions = data.get('total_questions')
    percentage = data.get('percentage')
    attempt_number = data.get('attempt_number')
    submitted_answers = data.get('submitted_answers', [])
    correct_answers = data.get('correct_answers', [])
    submitted_at = data.get('submitted_at')

    try:
        excel_data = ExcelExporter.create_exam_report(
            student_name=student_name,
            chapter_name=chapter_name,
            score=score,
            total_questions=total_questions,
            percentage=percentage,
            attempt_number=attempt_number,
            submitted_answers=submitted_answers,
            correct_answers=correct_answers,
            submitted_at=submitted_at
        )

        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"OMR_Report_{student_name}_{chapter_name}_{timestamp}.xlsx"

        return send_file(
            BytesIO(excel_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/export/chapter-results', methods=['POST'])
def export_chapter_results():
    """Export all results for a chapter as Excel"""
    data = request.json
    chapter_name = data.get('chapter_name')

    if not chapter_name:
        return jsonify({'success': False, 'message': 'Chapter name required'}), 400

    conn = get_db()

    # Get all attempts for this chapter
    attempts = conn.execute('''
        SELECT a.*, c.chapter_name, c.correct_answers, c.num_questions
        FROM attempts a
        JOIN chapters c ON a.chapter_id = c.id
        WHERE c.chapter_name = ?
        ORDER BY a.submitted_at DESC
    ''', (chapter_name,)).fetchall()

    if not attempts:
        return jsonify({'success': False, 'message': 'No results found'}), 404

    try:
        # Create Excel with multiple sheets (one per attempt or summary sheet)
        output = BytesIO()
        import pandas as pd
        from xlsxwriter import Workbook

        workbook = Workbook(output)
        summary_sheet = workbook.add_worksheet('Summary')

        # Add summary data
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#6366f1',
            'font_color': 'white',
            'border': 1
        })

        summary_sheet.write('A1', 'Chapter Name', header_format)
        summary_sheet.write('B1', 'Student Name', header_format)
        summary_sheet.write('C1', 'Attempt', header_format)
        summary_sheet.write('D1', 'Score', header_format)
        summary_sheet.write('E1', 'Percentage', header_format)
        summary_sheet.write('F1', 'Submitted At', header_format)

        row = 1
        for attempt in attempts:
            correct_answers = json.loads(attempt['correct_answers'])
            num_questions = attempt['num_questions']
            percentage = (attempt['score'] / num_questions *
                          100) if num_questions > 0 else 0

            summary_sheet.write(row, 0, attempt['chapter_name'])
            summary_sheet.write(row, 1, attempt['student_name'])
            summary_sheet.write(row, 2, attempt['attempt_number'])
            summary_sheet.write(row, 3, f"{attempt['score']}/{num_questions}")
            summary_sheet.write(row, 4, f"{percentage:.2f}%")
            summary_sheet.write(row, 5, attempt['submitted_at'])
            row += 1

        # Set column widths
        summary_sheet.set_column('A:A', 20)
        summary_sheet.set_column('B:B', 20)
        summary_sheet.set_column('C:C', 12)
        summary_sheet.set_column('D:D', 12)
        summary_sheet.set_column('E:E', 15)
        summary_sheet.set_column('F:F', 25)

        workbook.close()
        output.seek(0)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Chapter_Results_{chapter_name}_{timestamp}.xlsx"

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
