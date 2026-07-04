-- Database Schema for Student Result Management System

-- Drop tables if they exist to start fresh
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS students;

-- Students table
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    class_name TEXT NOT NULL
);

-- Users table (for authentication)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL, -- Will store pbkdf2:sha256 hashed password
    role TEXT NOT NULL CHECK (role IN ('admin', 'student')),
    student_id INTEGER DEFAULT NULL,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
);

-- Subjects table
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_code TEXT UNIQUE NOT NULL,
    subject_name TEXT NOT NULL,
    credits INTEGER NOT NULL DEFAULT 3 CHECK (credits > 0)
);

-- Results table
CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    marks REAL NOT NULL CHECK (marks >= 0 AND marks <= 100),
    grade TEXT NOT NULL,
    grade_point REAL NOT NULL CHECK (grade_point >= 0.0 AND grade_point <= 4.0),
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE,
    UNIQUE(student_id, subject_id)
);
