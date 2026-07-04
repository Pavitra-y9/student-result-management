import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'edugrade-secret-super-key-2026')

# -------------------------------------------------------------
# Grading & GPA Calculation Logic
# -------------------------------------------------------------

def calculate_grade_and_gp(marks):
    """Maps numerical marks (0-100) to Letter Grade and GPA Points (4.0 scale)."""
    try:
        m = float(marks)
    except (ValueError, TypeError):
        return 'F', 0.0
        
    if m >= 90:
        return 'A', 4.0
    elif m >= 80:
        return 'B', 3.0
    elif m >= 70:
        return 'C', 2.0
    elif m >= 60:
        return 'D', 1.0
    else:
        return 'F', 0.0

# -------------------------------------------------------------
# Authorization Decorators
# -------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash("Access denied. Administration privileges required.", "danger")
            # Redirect to their appropriate dashboard if logged in
            if session.get('role') == 'student':
                return redirect(url_for('student_dashboard'))
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('login'))
        if session.get('role') != 'student':
            flash("Access denied. Student portal access required.", "danger")
            if session.get('role') == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# -------------------------------------------------------------
# General Routes (Index, Login, Logout)
# -------------------------------------------------------------

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session.get('role') == 'student':
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash("Please fill in all login fields.", "danger")
            return render_template('login.html')
            
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            # Create session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['student_id'] = user['student_id']
            
            flash(f"Welcome back, {user['username']}!", "success")
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash("Invalid username or password. Please try again.", "danger")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have successfully signed out.", "success")
    return redirect(url_for('login'))

# -------------------------------------------------------------
# Admin Dashboard & Statistics
# -------------------------------------------------------------

@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Total Students
    cursor.execute("SELECT COUNT(*) as count FROM students")
    total_students = cursor.fetchone()['count']
    
    # 2. Total Subjects
    cursor.execute("SELECT COUNT(*) as count FROM subjects")
    total_subjects = cursor.fetchone()['count']
    
    # 3. Total Results Count
    cursor.execute("SELECT COUNT(*) as count FROM results")
    total_results = cursor.fetchone()['count']
    
    # 4. GPA Calculations (Average school-wide GPA)
    # Get all results grouped by student
    cursor.execute('''
        SELECT r.student_id, r.grade_point, s.credits
        FROM results r
        JOIN subjects s ON r.subject_id = s.id
    ''')
    rows = cursor.fetchall()
    
    student_totals = {}
    for row in rows:
        sid = row['student_id']
        gp = row['grade_point']
        credits = row['credits']
        if sid not in student_totals:
            student_totals[sid] = {'weighted_gp': 0.0, 'total_credits': 0}
        student_totals[sid]['weighted_gp'] += gp * credits
        student_totals[sid]['total_credits'] += credits
        
    gpas = []
    for sid, data in student_totals.items():
        if data['total_credits'] > 0:
            gpas.append(data['weighted_gp'] / data['total_credits'])
            
    avg_gpa = sum(gpas) / len(gpas) if gpas else 0.0
    
    # 5. Top 5 Students by GPA
    cursor.execute("SELECT id, roll_no, name, class_name FROM students")
    all_students = cursor.fetchall()
    
    student_gpa_list = []
    for s in all_students:
        cursor.execute('''
            SELECT r.grade_point, sub.credits
            FROM results r
            JOIN subjects sub ON r.subject_id = sub.id
            WHERE r.student_id = ?
        ''', (s['id'],))
        s_results = cursor.fetchall()
        
        weighted = 0.0
        credits = 0
        for r in s_results:
            weighted += r['grade_point'] * r['credits']
            credits += r['credits']
            
        if credits > 0:
            student_gpa_list.append({
                'roll_no': s['roll_no'],
                'name': s['name'],
                'class_name': s['class_name'],
                'gpa': weighted / credits
            })
            
    # Sort descending
    student_gpa_list.sort(key=lambda x: x['gpa'], reverse=True)
    top_students = student_gpa_list[:5]
    
    stats = {
        'total_students': total_students,
        'total_subjects': total_subjects,
        'total_results': total_results,
        'avg_gpa': avg_gpa
    }
    
    conn.close()
    return render_template('admin_dashboard.html', stats=stats, top_students=top_students)

# -------------------------------------------------------------
# Admin: Students CRUD
# -------------------------------------------------------------

@app.route('/admin/students', methods=['GET'])
@admin_required
def admin_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch student list
    cursor.execute("SELECT * FROM students ORDER BY id DESC")
    students = cursor.fetchall()
    
    # Check if we are in Edit Mode
    edit_student_id = request.args.get('edit')
    edit_student = None
    if edit_student_id:
        cursor.execute("SELECT * FROM students WHERE id = ?", (edit_student_id,))
        edit_student = cursor.fetchone()
        
    conn.close()
    return render_template('admin_students.html', students=students, edit_student=edit_student)

@app.route('/admin/students/add', methods=['POST'])
@admin_required
def admin_add_student():
    roll_no = request.form.get('roll_no', '').strip()
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    class_name = request.form.get('class_name', '').strip()
    
    if not (roll_no and name and email and class_name):
        flash("All fields are required to register a student.", "danger")
        return redirect(url_for('admin_students'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Insert student
        cursor.execute(
            "INSERT INTO students (roll_no, name, email, class_name) VALUES (?, ?, ?, ?)",
            (roll_no, name, email, class_name)
        )
        student_id = cursor.lastrowid
        
        # 2. Insert user account
        default_pwd = generate_password_hash('student123')
        cursor.execute(
            "INSERT INTO users (username, password, role, student_id) VALUES (?, ?, ?, ?)",
            (roll_no, default_pwd, 'student', student_id)
        )
        conn.commit()
        flash(f"Student '{name}' registered successfully. Default password is 'student123'.", "success")
    except sqlite3.IntegrityError:
        conn.rollback()
        flash(f"Integrity Error: Roll number '{roll_no}' is already registered.", "danger")
    finally:
        conn.close()
        
    return redirect(url_for('admin_students'))

@app.route('/admin/students/edit/<int:student_id>', methods=['POST'])
@admin_required
def admin_edit_student(student_id):
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    class_name = request.form.get('class_name', '').strip()
    
    if not (name and email and class_name):
        flash("Fields cannot be empty during update.", "danger")
        return redirect(url_for('admin_students', edit=student_id))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE students SET name = ?, email = ?, class_name = ? WHERE id = ?",
            (name, email, class_name, student_id)
        )
        conn.commit()
        flash("Student details updated successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error updating details: {str(e)}", "danger")
    finally:
        conn.close()
        
    return redirect(url_for('admin_students'))

@app.route('/admin/students/delete/<int:student_id>', methods=['POST'])
@admin_required
def admin_delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        flash("Student and their associated data deleted successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error executing deletion: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin_students'))

# -------------------------------------------------------------
# Admin: Subjects CRUD
# -------------------------------------------------------------

@app.route('/admin/subjects', methods=['GET'])
@admin_required
def admin_subjects():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects ORDER BY subject_code ASC")
    subjects = cursor.fetchall()
    
    edit_subject_id = request.args.get('edit')
    edit_subject = None
    if edit_subject_id:
        cursor.execute("SELECT * FROM subjects WHERE id = ?", (edit_subject_id,))
        edit_subject = cursor.fetchone()
        
    conn.close()
    return render_template('admin_subjects.html', subjects=subjects, edit_subject=edit_subject)

@app.route('/admin/subjects/add', methods=['POST'])
@admin_required
def admin_add_subject():
    code = request.form.get('subject_code', '').strip().upper()
    name = request.form.get('subject_name', '').strip()
    try:
        credits = int(request.form.get('credits', 3))
    except ValueError:
        credits = 3
        
    if not (code and name):
        flash("Please provide both subject code and subject name.", "danger")
        return redirect(url_for('admin_subjects'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO subjects (subject_code, subject_name, credits) VALUES (?, ?, ?)",
            (code, name, credits)
        )
        conn.commit()
        flash(f"Subject '{code} - {name}' added successfully.", "success")
    except sqlite3.IntegrityError:
        conn.rollback()
        flash(f"Integrity Error: Subject Code '{code}' already exists.", "danger")
    finally:
        conn.close()
        
    return redirect(url_for('admin_subjects'))

@app.route('/admin/subjects/edit/<int:subject_id>', methods=['POST'])
@admin_required
def admin_edit_subject(subject_id):
    code = request.form.get('subject_code', '').strip().upper()
    name = request.form.get('subject_name', '').strip()
    try:
        credits = int(request.form.get('credits', 3))
    except ValueError:
        credits = 3
        
    if not (code and name):
        flash("Fields cannot be empty during update.", "danger")
        return redirect(url_for('admin_subjects', edit=subject_id))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE subjects SET subject_code = ?, subject_name = ?, credits = ? WHERE id = ?",
            (code, name, credits, subject_id)
        )
        conn.commit()
        flash("Subject details updated successfully.", "success")
    except sqlite3.IntegrityError:
        conn.rollback()
        flash(f"Integrity Error: Subject code '{code}' conflicts with another subject.", "danger")
    finally:
        conn.close()
        
    return redirect(url_for('admin_subjects'))

@app.route('/admin/subjects/delete/<int:subject_id>', methods=['POST'])
@admin_required
def admin_delete_subject(subject_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
        flash("Subject and associated marks records deleted successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error executing deletion: {str(e)}", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin_subjects'))

# -------------------------------------------------------------
# Admin: Results CRUD
# -------------------------------------------------------------

@app.route('/admin/results', methods=['GET'])
@admin_required
def admin_results():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch Lists for Select Dropdowns
    cursor.execute("SELECT id, roll_no, name, class_name FROM students ORDER BY name ASC")
    students = cursor.fetchall()
    
    cursor.execute("SELECT id, subject_code, subject_name, credits FROM subjects ORDER BY subject_code ASC")
    subjects = cursor.fetchall()
    
    # 2. Check filters
    selected_student_id = request.args.get('student_filter')
    selected_student = None
    calculated_gpa = 0.0
    
    # 3. Check edit mode
    edit_result_id = request.args.get('edit')
    edit_result = None
    
    if edit_result_id:
        # Load single grade details for edit form
        cursor.execute('''
            SELECT r.id, r.student_id, r.subject_id, r.marks, r.grade, r.grade_point,
                   s.roll_no, s.name as student_name, sub.subject_code, sub.subject_name
            FROM results r
            JOIN students s ON r.student_id = s.id
            JOIN subjects sub ON r.subject_id = sub.id
            WHERE r.id = ?
        ''', (edit_result_id,))
        edit_result = cursor.fetchone()
        
    # 4. Query results table
    if selected_student_id:
        cursor.execute("SELECT * FROM students WHERE id = ?", (selected_student_id,))
        selected_student = cursor.fetchone()
        
        cursor.execute('''
            SELECT r.id, r.marks, r.grade, r.grade_point,
                   s.roll_no, s.name as student_name, 
                   sub.subject_code, sub.subject_name, sub.credits
            FROM results r
            JOIN students s ON r.student_id = s.id
            JOIN subjects sub ON r.subject_id = sub.id
            WHERE r.student_id = ?
            ORDER BY sub.subject_code ASC
        ''', (selected_student_id,))
        results = cursor.fetchall()
        
        # Calculate GPA for selected student
        weighted_sum = 0.0
        credit_sum = 0
        for r in results:
            weighted_sum += r['grade_point'] * r['credits']
            credit_sum += r['credits']
        calculated_gpa = weighted_sum / credit_sum if credit_sum > 0 else 0.0
    else:
        cursor.execute('''
            SELECT r.id, r.marks, r.grade, r.grade_point,
                   s.roll_no, s.name as student_name, 
                   sub.subject_code, sub.subject_name, sub.credits
            FROM results r
            JOIN students s ON r.student_id = s.id
            JOIN subjects sub ON r.subject_id = sub.id
            ORDER BY r.id DESC
        ''')
        results = cursor.fetchall()
        
    conn.close()
    return render_template(
        'admin_results.html', 
        students=students, 
        subjects=subjects, 
        results=results, 
        selected_student_id=selected_student_id,
        selected_student=selected_student,
        calculated_gpa=calculated_gpa,
        edit_result=edit_result
    )

@app.route('/admin/results/add', methods=['POST'])
@admin_required
def admin_add_result():
    student_id = request.form.get('student_id')
    subject_id = request.form.get('subject_id')
    marks_str = request.form.get('marks', '').strip()
    filter_redirect = request.form.get('filter_redirect', '')
    
    if not (student_id and subject_id and marks_str):
        flash("Please complete all input fields to record a grade.", "danger")
        return redirect(url_for('admin_results', student_filter=filter_redirect))
        
    try:
        marks = float(marks_str)
        if marks < 0 or marks > 100:
            raise ValueError
    except ValueError:
        flash("Marks must be a valid decimal number between 0.0 and 100.0.", "danger")
        return redirect(url_for('admin_results', student_filter=filter_redirect))
        
    grade, gp = calculate_grade_and_gp(marks)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Upsert: If the student already has a mark recorded for this course, replace it
        cursor.execute('''
            INSERT INTO results (student_id, subject_id, marks, grade, grade_point)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(student_id, subject_id) 
            DO UPDATE SET 
                marks = excluded.marks,
                grade = excluded.grade,
                grade_point = excluded.grade_point
        ''', (student_id, subject_id, marks, grade, gp))
        conn.commit()
        flash("Result recorded and GPA updated successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error submitting result: {str(e)}", "danger")
    finally:
        conn.close()
        
    return redirect(url_for('admin_results', student_filter=filter_redirect))

@app.route('/admin/results/edit/<int:result_id>', methods=['POST'])
@admin_required
def admin_edit_result(result_id):
    marks_str = request.form.get('marks', '').strip()
    
    # Extract filter redirect if present
    filter_redirect = request.args.get('student_filter', '')
    
    try:
        marks = float(marks_str)
        if marks < 0 or marks > 100:
            raise ValueError
    except ValueError:
        flash("Marks must be a valid number between 0.0 and 100.0.", "danger")
        return redirect(url_for('admin_results', edit=result_id, student_filter=filter_redirect))
        
    grade, gp = calculate_grade_and_gp(marks)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE results SET marks = ?, grade = ?, grade_point = ? WHERE id = ?",
            (marks, grade, gp, result_id)
        )
        conn.commit()
        flash("Student exam score updated successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error executing update: {str(e)}", "danger")
    finally:
        conn.close()
        
    return redirect(url_for('admin_results', student_filter=filter_redirect))

@app.route('/admin/results/delete/<int:result_id>', methods=['POST'])
@admin_required
def admin_delete_result(result_id):
    filter_redirect = request.form.get('filter_redirect', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM results WHERE id = ?", (result_id,))
        conn.commit()
        flash("Result record removed successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error deleting record: {str(e)}", "danger")
    finally:
        conn.close()
        
    return redirect(url_for('admin_results', student_filter=filter_redirect))

# -------------------------------------------------------------
# Student Portal Dashboard & Profile
# -------------------------------------------------------------

@app.route('/student')
@student_required
def student_dashboard():
    student_id = session.get('student_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch student info
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    
    # 2. Fetch student grades
    cursor.execute('''
        SELECT r.marks, r.grade, r.grade_point, sub.subject_code, sub.subject_name, sub.credits
        FROM results r
        JOIN subjects sub ON r.subject_id = sub.id
        WHERE r.student_id = ?
        ORDER BY sub.subject_code ASC
    ''', (student_id,))
    results = cursor.fetchall()
    
    # 3. Calculate GPA
    weighted_sum = 0.0
    credit_sum = 0
    for r in results:
        weighted_sum += r['grade_point'] * r['credits']
        credit_sum += r['credits']
    gpa = weighted_sum / credit_sum if credit_sum > 0 else 0.0
    
    conn.close()
    return render_template('student_dashboard.html', student=student, results=results, gpa=gpa)

@app.route('/student/change_password', methods=['GET', 'POST'])
@student_required
def student_change_password():
    if request.method == 'POST':
        curr_pwd = request.form.get('current_password', '')
        new_pwd = request.form.get('new_password', '')
        confirm_pwd = request.form.get('confirm_password', '')
        
        if not (curr_pwd and new_pwd and confirm_pwd):
            flash("All password fields are required.", "danger")
            return redirect(url_for('student_change_password'))
            
        if new_pwd != confirm_pwd:
            flash("New password and confirmation password do not match.", "danger")
            return redirect(url_for('student_change_password'))
            
        if len(new_pwd) < 6:
            flash("Password must be at least 6 characters in length.", "danger")
            return redirect(url_for('student_change_password'))
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify current password
        cursor.execute("SELECT password FROM users WHERE id = ?", (session.get('user_id'),))
        user_db = cursor.fetchone()
        
        if user_db and check_password_hash(user_db['password'], curr_pwd):
            # Update password
            new_hash = generate_password_hash(new_pwd)
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_hash, session.get('user_id')))
            conn.commit()
            flash("Your account password has been changed successfully.", "success")
            conn.close()
            return redirect(url_for('student_dashboard'))
        else:
            flash("Current password verification failed. Please try again.", "danger")
            conn.close()
            
    return render_template('student_change_password.html')

# -------------------------------------------------------------
# App Loader
# -------------------------------------------------------------

if __name__ == '__main__':
    # Initialize the database on startup if database.db doesn't exist
    db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
    if not os.path.exists(db_file):
        from database import init_db
        init_db()
        
    app.run(debug=True)
