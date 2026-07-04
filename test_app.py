import os
import unittest
import sqlite3
from app import app, calculate_grade_and_gp
from database import init_db, get_db_connection

class StudentResultSystemTestCase(unittest.TestCase):

    def setUp(self):
        """Set up a test environment: use a temporary database copy or reset the DB."""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = app.test_client()
        
        # Re-initialize database to ensure clean state
        init_db()

    def tearDown(self):
        """Clean up database after each test."""
        # Clean up database tables
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM results;")
        cursor.execute("DELETE FROM subjects;")
        cursor.execute("DELETE FROM users WHERE username != 'admin';")
        cursor.execute("DELETE FROM students;")
        conn.commit()
        conn.close()

    def login(self, username, password):
        """Helper to post credentials to the login route."""
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        """Helper to log out."""
        return self.client.get('/logout', follow_redirects=True)

    # -------------------------------------------------------------
    # Test 1: Grading Mapping & GP Calculation
    # -------------------------------------------------------------
    def test_grading_logic(self):
        """Verify grade mapping logic maps marks to correct Letter and Grade Point."""
        self.assertEqual(calculate_grade_and_gp(95), ('A', 4.0))
        self.assertEqual(calculate_grade_and_gp(90), ('A', 4.0))
        self.assertEqual(calculate_grade_and_gp(85), ('B', 3.0))
        self.assertEqual(calculate_grade_and_gp(80), ('B', 3.0))
        self.assertEqual(calculate_grade_and_gp(75), ('C', 2.0))
        self.assertEqual(calculate_grade_and_gp(70), ('C', 2.0))
        self.assertEqual(calculate_grade_and_gp(65), ('D', 1.0))
        self.assertEqual(calculate_grade_and_gp(60), ('D', 1.0))
        self.assertEqual(calculate_grade_and_gp(59.9), ('F', 0.0))
        self.assertEqual(calculate_grade_and_gp(0), ('F', 0.0))
        # Handle string or error inputs gracefully
        self.assertEqual(calculate_grade_and_gp("invalid"), ('F', 0.0))

    # -------------------------------------------------------------
    # Test 2: Authentication & Sessions
    # -------------------------------------------------------------
    def test_admin_login_success(self):
        """Verify admin can log in with default credentials."""
        response = self.login('admin', 'admin123')
        self.assertIn(b'Admin Dashboard', response.data)
        self.assertIn(b'Welcome back, admin!', response.data)

    def test_admin_login_failure(self):
        """Verify login fails with wrong password."""
        response = self.login('admin', 'wrongpassword')
        self.assertIn(b'Invalid username or password', response.data)

    def test_route_guards_redirect_anonymous(self):
        """Verify non-logged-in users cannot access dashboards."""
        response = self.client.get('/admin', follow_redirects=True)
        self.assertIn(b'Please sign in to access this page', response.data)
        
        response = self.client.get('/student', follow_redirects=True)
        self.assertIn(b'Please sign in to access this page', response.data)

    # -------------------------------------------------------------
    # Test 3: Students CRUD Operations
    # -------------------------------------------------------------
    def test_admin_student_crud(self):
        """Test adding, editing, and deleting students as admin."""
        # Log in as admin
        self.login('admin', 'admin123')
        
        # 1. Add Student
        response = self.client.post('/admin/students/add', data=dict(
            roll_no='STU1001',
            name='Test Student',
            email='test@student.com',
            class_name='CS-2026'
        ), follow_redirects=True)
        
        self.assertIn(b'Student &#39;Test Student&#39; registered successfully', response.data)
        self.assertIn(b'STU1001', response.data)
        self.assertIn(b'Test Student', response.data)
        
        # Verify student exists in DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE roll_no = 'STU1001'")
        student = cursor.fetchone()
        self.assertIsNotNone(student)
        student_id = student['id']
        
        # Verify portal user account was automatically created
        cursor.execute("SELECT * FROM users WHERE username = 'STU1001'")
        user = cursor.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user['role'], 'student')
        self.assertEqual(user['student_id'], student_id)
        
        # 2. Edit Student
        response = self.client.post(f'/admin/students/edit/{student_id}', data=dict(
            name='Test Student Updated',
            email='updated@student.com',
            class_name='CS-2027'
        ), follow_redirects=True)
        
        self.assertIn(b'Student details updated successfully', response.data)
        self.assertIn(b'Test Student Updated', response.data)
        self.assertIn(b'updated@student.com', response.data)
        
        # 3. Delete Student
        response = self.client.post(f'/admin/students/delete/{student_id}', follow_redirects=True)
        self.assertIn(b'Student and their associated data deleted successfully', response.data)
        
        # Verify user account and student records are deleted
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        self.assertIsNone(cursor.fetchone())
        cursor.execute("SELECT * FROM users WHERE username = 'STU1001'")
        self.assertIsNone(cursor.fetchone())
        
        conn.close()

    # -------------------------------------------------------------
    # Test 4: GPA Calculations and Results Tracking
    # -------------------------------------------------------------
    def test_gpa_calculations(self):
        """Verify marks entry and dynamic credit-weighted GPA calculation."""
        self.login('admin', 'admin123')
        
        # 1. Add Student
        self.client.post('/admin/students/add', data=dict(
            roll_no='GPA101',
            name='GPA Student',
            email='gpa@student.com',
            class_name='CS-2026'
        ))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM students WHERE roll_no = 'GPA101'")
        student_id = cursor.fetchone()['id']
        
        # 2. Add Subjects
        self.client.post('/admin/subjects/add', data=dict(
            subject_code='CS101',
            subject_name='Programming Python',
            credits=4
        ))
        self.client.post('/admin/subjects/add', data=dict(
            subject_code='MA102',
            subject_name='Calculus',
            credits=3
        ))
        
        cursor.execute("SELECT id FROM subjects WHERE subject_code = 'CS101'")
        cs_id = cursor.fetchone()['id']
        cursor.execute("SELECT id FROM subjects WHERE subject_code = 'MA102'")
        ma_id = cursor.fetchone()['id']
        
        # 3. Enter Results
        # CS101: 95 marks -> A (4.0) -> Weighted GP = 4.0 * 4 = 16.0
        self.client.post('/admin/results/add', data=dict(
            student_id=student_id,
            subject_id=cs_id,
            marks=95
        ))
        # MA102: 75 marks -> C (2.0) -> Weighted GP = 2.0 * 3 = 6.0
        # Expected GPA = (16.0 + 6.0) / (4 + 3) = 22.0 / 7 = 3.14
        self.client.post('/admin/results/add', data=dict(
            student_id=student_id,
            subject_id=ma_id,
            marks=75
        ))
        
        # 4. Check GPA on Admin Results Filter View
        response = self.client.get(f'/admin/results?student_filter={student_id}')
        self.assertIn(b'3.14', response.data)
        
        # 5. Check GPA on Student Dashboard (after logging in as student)
        self.logout()
        # Log in as the student
        response = self.login('GPA101', 'student123')
        self.assertIn(b'GPA Student', response.data)
        self.assertIn(b'3.14', response.data)
        self.assertIn(b'CS101', response.data)
        self.assertIn(b'Programming Python', response.data)
        self.assertIn(b'MA102', response.data)
        
        conn.close()

if __name__ == '__main__':
    unittest.main()
