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

    c.execute('''CREATE TABLE IF NOT EXISTS chapters
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  chapter_name TEXT UNIQUE NOT NULL,
                  num_questions INTEGER NOT NULL,
                  num_options INTEGER NOT NULL,
                  correct_answers TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS attempts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  chapter_id INTEGER NOT NULL,
                  student_name TEXT NOT NULL,
                  submitted_answers TEXT NOT NULL,
                  score REAL NOT NULL,
                  total_questions INTEGER NOT NULL,
                  attempt_number INTEGER NOT NULL,
                  time_taken INTEGER DEFAULT 0,
                  submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (chapter_id) REFERENCES chapters(id))''')

    # Add time_taken column if it doesn't exist (for database migration)
    try:
        c.execute('SELECT time_taken FROM attempts LIMIT 1')
    except sqlite3.OperationalError:
        c.execute('ALTER TABLE attempts ADD COLUMN time_taken INTEGER DEFAULT 0')

    conn.commit()
    conn.close()

# API Routes

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/api/chapters', methods=['GET'])
def get_chapters():
    """Get all chapters"""
    conn = get_db()
    chapters = conn.execute('SELECT * FROM chapters ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(ch) for ch in chapters])

@app.route('/api/chapter/<int:chapter_id>', methods=['GET'])
def get_chapter(chapter_id):
    """Get chapter details"""
    conn = get_db()
    chapter = conn.execute('SELECT * FROM chapters WHERE id = ?', (chapter_id,)).fetchone()
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

    conn = get_db()
    
    # Get chapter details
    chapter = conn.execute('SELECT * FROM chapters WHERE id = ?', (chapter_id,)).fetchone()
    if not chapter:
        return jsonify({'success': False, 'message': 'Chapter not found'}), 404

    correct_answers = json.loads(chapter['correct_answers'])
    
    # Calculate score
    score = sum(1 for i, ans in enumerate(submitted_answers) if ans == correct_answers[i])
    
    # Get attempt number
    attempt = conn.execute(
        'SELECT MAX(attempt_number) as max_attempt FROM attempts WHERE chapter_id = ? AND student_name = ?',
        (chapter_id, student_name)
    ).fetchone()
    attempt_number = (attempt['max_attempt'] or 0) + 1
    
    # Save attempt
    conn.execute(
        '''INSERT INTO attempts (chapter_id, student_name, submitted_answers, score, total_questions, attempt_number, time_taken)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (chapter_id, student_name, json.dumps(submitted_answers), score, len(correct_answers), attempt_number, time_taken)
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
    
    # Base query with optional student filter
    student_where = f"WHERE a.student_name = '{student_filter}'" if student_filter else ""
    
    # Overall stats
    chapters_count = conn.execute('SELECT COUNT(*) as count FROM chapters').fetchone()['count']
    attempts_count = conn.execute(f'SELECT COUNT(*) as count FROM attempts {student_where}').fetchone()['count']
    students_count = conn.execute('SELECT COUNT(DISTINCT student_name) as count FROM attempts').fetchone()['count']
    
    # Average score
    avg_result = conn.execute(f'''
        SELECT AVG(CAST(score as FLOAT) / total_questions * 100) as avg_percentage,
               MAX(CAST(score as FLOAT) / total_questions * 100) as best_score,
               AVG(CAST(score as FLOAT) / total_questions) as avg_accuracy
        FROM attempts
        {student_where}
    ''').fetchone()
    avg_percentage = avg_result['avg_percentage'] or 0
    best_score = avg_result['best_score'] or 0
    avg_accuracy = (avg_result['avg_accuracy'] or 0) * 100
    
    # Convert best_score to points (e.g., out of the total in last attempt)
    best_score_points = conn.execute(f'''
        SELECT MAX(score) as max_score FROM attempts {student_where}
    ''').fetchone()['max_score'] or 0
    
    # Chapter-wise stats
    chapter_stats_raw = conn.execute(f'''
        SELECT c.id, c.chapter_name, COUNT(a.id) as total_attempts, 
               MAX(CAST(a.score as FLOAT)) as best_score,
               AVG(CAST(a.score as FLOAT) / a.total_questions * 100) as avg_percentage,
               AVG(CAST(a.score as FLOAT) / a.total_questions) as avg_accuracy,
               COUNT(DISTINCT a.student_name) as unique_students
        FROM chapters c
        LEFT JOIN attempts a ON c.id = a.chapter_id
        {'' if not student_filter else f"AND a.student_name = '{student_filter}'"}
        GROUP BY c.id
        ORDER BY total_attempts DESC
    ''').fetchall()
    
    chapter_stats = []
    for stat in chapter_stats_raw:
        chapter_stats.append({
            'chapter_name': stat['chapter_name'],
            'total_attempts': stat['total_attempts'] or 0,
            'best_score': stat['best_score'] or 0,
            'avg_percentage': stat['avg_percentage'] or 0,
            'avg_accuracy': (stat['avg_accuracy'] or 0) * 100
        })
    
    # Top students
    top_students = conn.execute('''
        SELECT student_name, COUNT(*) as attempts,
               SUM(score) as total_score, SUM(total_questions) as total_questions,
               ROUND(CAST(SUM(score) as FLOAT) / SUM(total_questions) * 100, 2) as percentage
        FROM attempts
        GROUP BY student_name
        ORDER BY percentage DESC
        LIMIT 10
    ''').fetchall()
    
    # All attempts with details for charts and detailed stats
    all_attempts = conn.execute(f'''
        SELECT a.id, a.student_name, a.attempt_number, c.chapter_name, c.id as chapter_id,
               a.score, a.total_questions, COALESCE(a.time_taken, 0) as time_taken, a.submitted_at, a.submitted_answers as answers
        FROM attempts a
        JOIN chapters c ON a.chapter_id = c.id
        {student_where}
        ORDER BY a.submitted_at DESC
    ''').fetchall()
    
    conn.close()
    
    return jsonify({
        'chapters': chapters_count,
        'attempts': attempts_count,
        'students': students_count,
        'total_attempts': attempts_count,
        'avg_score': round(avg_percentage, 2),
        'avg_percentage': round(avg_percentage, 2),
        'best_score': best_score_points,
        'avg_accuracy': round(avg_accuracy, 2),
        'chapter_stats': chapter_stats,
        'top_students': [dict(student) for student in top_students],
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
            percentage = (attempt['score'] / num_questions * 100) if num_questions > 0 else 0
            
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
