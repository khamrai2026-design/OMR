import unittest
import os
import sqlite3
import json
import datetime
import web_app


class AnalyticsFilterTest(unittest.TestCase):
    TEST_DB = 'test_analytics.db'

    @classmethod
    def setUpClass(cls):
        # Configure app to use test database
        web_app.DATABASE = cls.TEST_DB
        web_app.app.config['TESTING'] = True
        cls.client = web_app.app.test_client()

    def setUp(self):
        # Reset database for each test
        if os.path.exists(self.TEST_DB):
            os.remove(self.TEST_DB)

        # Initialize schema
        self.init_test_db()

        # Seed data
        self.seed_data()

    def tearDown(self):
        if os.path.exists(self.TEST_DB):
            os.remove(self.TEST_DB)

    def init_test_db(self):
        with web_app.app.app_context():
            web_app.init_db()

    def seed_data(self):
        conn = sqlite3.connect(self.TEST_DB)
        c = conn.cursor()

        # 1. Create Subjects
        # Subject 1: Math
        c.execute("INSERT INTO subjects (subject_name) VALUES ('Math')")
        self.math_id = c.lastrowid

        # Subject 2: Science
        c.execute("INSERT INTO subjects (subject_name) VALUES ('Science')")
        self.science_id = c.lastrowid

        # 2. Create Chapters
        # Ch 1: Algebra (Math)
        c.execute("""
            INSERT INTO chapters (subject_id, chapter_name, num_questions, num_options, correct_answers) 
            VALUES (?, 'Algebra', 5, 4, '["A","B","C","D","A"]')
        """, (self.math_id,))
        self.algebra_id = c.lastrowid

        # Ch 2: Geometry (Math)
        c.execute("""
            INSERT INTO chapters (subject_id, chapter_name, num_questions, num_options, correct_answers) 
            VALUES (?, 'Geometry', 5, 4, '["A","A","A","A","A"]')
        """, (self.math_id,))
        self.geometry_id = c.lastrowid

        # Ch 3: Physics (Science)
        c.execute("""
            INSERT INTO chapters (subject_id, chapter_name, num_questions, num_options, correct_answers) 
            VALUES (?, 'Physics', 5, 4, '["B","B","B","B","B"]')
        """, (self.science_id,))
        self.physics_id = c.lastrowid

        # 3. Create Attempts
        # Attempt 1: Algebra - Today - Score 5/5
        today = datetime.datetime.now()
        c.execute("""
            INSERT INTO attempts (chapter_id, student_name, submitted_answers, score, total_questions, attempt_number, submitted_at)
            VALUES (?, 'Student1', '["A","B","C","D","A"]', 5, 5, 1, ?)
        """, (self.algebra_id, today))

        # Attempt 2: Geometry - Today - Score 0/5
        c.execute("""
            INSERT INTO attempts (chapter_id, student_name, submitted_answers, score, total_questions, attempt_number, submitted_at)
            VALUES (?, 'Student1', '["B","B","B","B","B"]', 0, 5, 1, ?)
        """, (self.geometry_id, today))

        # Attempt 3: Physics - 60 days ago - Score 5/5
        old_date = today - datetime.timedelta(days=60)
        c.execute("""
            INSERT INTO attempts (chapter_id, student_name, submitted_answers, score, total_questions, attempt_number, submitted_at)
            VALUES (?, 'Student1', '["B","B","B","B","B"]', 5, 5, 1, ?)
        """, (self.physics_id, old_date))

        conn.commit()
        conn.close()

    def test_no_filters(self):
        """Test API returns all data when no filters provided"""
        response = self.client.get('/api/analytics')
        data = json.loads(response.data)

        # Should have 3 attempts total
        self.assertEqual(data['total_attempts'], 3)
        # Avg score: (5 + 0 + 5) / 15 * 100 approx
        # Wait, avg score calculation in app is: AVG(score/total * 100)
        # Attempt 1: 100%, Attempt 2: 0%, Attempt 3: 100%. Avg: 66.67%
        self.assertAlmostEqual(data['avg_score'], 66.67, places=2)

    def test_filter_by_subject(self):
        """Test API filters correctly by Subject ID"""
        # Filter for Math (ID 1)
        response = self.client.get(f'/api/analytics?subject_id={self.math_id}')
        data = json.loads(response.data)

        # Should have 2 Math attempts (Algebra, Geometry)
        self.assertEqual(data['total_attempts'], 2)
        # Avg score: (100% + 0%) / 2 = 50%
        self.assertEqual(data['avg_score'], 50.0)

        # Verify attempt list contains only Math chapters
        chapter_names = [a['chapter_name'] for a in data['all_attempts']]
        self.assertIn('Algebra', chapter_names)
        self.assertIn('Geometry', chapter_names)
        self.assertNotIn('Physics', chapter_names)

    def test_filter_by_chapter(self):
        """Test API filters correctly by Chapter ID"""
        # Filter for Algebra (ID 1)
        response = self.client.get(
            f'/api/analytics?chapter_id={self.algebra_id}')
        data = json.loads(response.data)

        # Should have 1 attempt
        self.assertEqual(data['total_attempts'], 1)
        # Score 100%
        self.assertEqual(data['avg_score'], 100.0)

        # Verify attempt list
        self.assertEqual(len(data['all_attempts']), 1)
        self.assertEqual(data['all_attempts'][0]['chapter_name'], 'Algebra')

    def test_filter_by_date(self):
        """Test API filters correctly by Date (days)"""
        # Filter last 30 days (should exclude Physics which was 60 days ago)
        response = self.client.get('/api/analytics?days=30')
        data = json.loads(response.data)

        # Should have 2 attempts (Algebra, Geometry)
        self.assertEqual(data['total_attempts'], 2)
        # Physics should be excluded
        chapter_names = [a['chapter_name'] for a in data['all_attempts']]
        self.assertNotIn('Physics', chapter_names)

    def test_combined_filters(self):
        """Test Subject + Date filters together"""
        # Filter Math + Last 30 days
        response = self.client.get(
            f'/api/analytics?subject_id={self.math_id}&days=30')
        data = json.loads(response.data)

        # Should have 2 attempts
        self.assertEqual(data['total_attempts'], 2)

        # Filter Science + Last 30 days (Should be empty, Science attempt is old)
        response = self.client.get(
            f'/api/analytics?subject_id={self.science_id}&days=30')
        data = json.loads(response.data)

        self.assertEqual(data['total_attempts'], 0)


if __name__ == '__main__':
    unittest.main()
