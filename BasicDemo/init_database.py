#!/usr/bin/env python3
"""
SQLite Database Initialization Script
This script creates and initializes an SQLite database with sample tables.
"""

import sqlite3
import os
from datetime import datetime

def create_database(db_name="project.db"):
    """
    Create and initialize SQLite database with sample tables
    """
    # Remove existing database if it exists
    if os.path.exists(db_name):
        print(f"Removing existing database: {db_name}")
        os.remove(db_name)
    
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    print(f"Creating database: {db_name}")
    
    # Create students table (example for a course project)
    cursor.execute('''
        CREATE TABLE students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            enrollment_date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("Created 'students' table")
    
    # Create courses table
    cursor.execute('''
        CREATE TABLE courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT UNIQUE NOT NULL,
            course_name TEXT NOT NULL,
            credits INTEGER DEFAULT 3,
            instructor TEXT,
            semester TEXT,
            year INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("Created 'courses' table")
    
    # Create enrollments table (many-to-many relationship)
    cursor.execute('''
        CREATE TABLE enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            enrollment_date DATE DEFAULT CURRENT_DATE,
            grade TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (course_id) REFERENCES courses (id),
            UNIQUE(student_id, course_id)
        )
    ''')
    print("Created 'enrollments' table")
    
    # Create assignments table
    cursor.execute('''
        CREATE TABLE assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date DATE,
            points INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses (id)
        )
    ''')
    print("Created 'assignments' table")
    
    # Insert sample data
    print("\nInserting sample data...")
    
    # Sample students
    students_data = [
        ('001', 'Alice', 'Johnson', 'alice.johnson@email.com'),
        ('002', 'Bob', 'Smith', 'bob.smith@email.com'),
        ('003', 'Carol', 'Williams', 'carol.williams@email.com'),
        ('004', 'David', 'Brown', 'david.brown@email.com')
    ]
    
    cursor.executemany('''
        INSERT INTO students (student_id, first_name, last_name, email)
        VALUES (?, ?, ?, ?)
    ''', students_data)
    
    # Sample courses
    courses_data = [
        ('IS330', 'Business Database Management', 3, 'Prof. Foster', 'Fall', 2025),
        ('CS101', 'Introduction to Programming', 3, 'Prof. Davis', 'Fall', 2025),
        ('MATH200', 'Statistics', 4, 'Prof. Wilson', 'Fall', 2025)
    ]
    
    cursor.executemany('''
        INSERT INTO courses (course_code, course_name, credits, instructor, semester, year)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', courses_data)
    
    # Sample assignments for IS330
    assignments_data = [
        (1, 'Database Design Project', 'Design a database schema for a business scenario', '2025-10-15', 100),
        (1, 'SQL Query Assignment', 'Write complex SQL queries for data analysis', '2025-10-30', 75),
        (1, 'Final Project', 'Implement a complete database application', '2025-12-10', 200)
    ]
    
    cursor.executemany('''
        INSERT INTO assignments (course_id, title, description, due_date, points)
        VALUES (?, ?, ?, ?, ?)
    ''', assignments_data)
    
    # Sample enrollments
    enrollments_data = [
        (1, 1),  # Alice -> IS330
        (2, 1),  # Bob -> IS330
        (3, 1),  # Carol -> IS330
        (4, 1),  # David -> IS330
        (1, 2),  # Alice -> CS101
        (2, 3)   # Bob -> MATH200
    ]
    
    cursor.executemany('''
        INSERT INTO enrollments (student_id, course_id)
        VALUES (?, ?)
    ''', enrollments_data)
    
    # Commit changes
    conn.commit()
    
    print(f"\nDatabase '{db_name}' created successfully!")
    print(f"Tables created: students, courses, enrollments, assignments")
    print(f"Sample data inserted for {len(students_data)} students and {len(courses_data)} courses")
    
    # Display some sample queries
    print("\n" + "="*50)
    print("SAMPLE QUERIES AND RESULTS:")
    print("="*50)
    
    # Query 1: List all students
    print("\n1. All Students:")
    cursor.execute("SELECT student_id, first_name, last_name, email FROM students")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} {row[2]} ({row[3]})")
    
    # Query 2: List all courses
    print("\n2. All Courses:")
    cursor.execute("SELECT course_code, course_name, instructor FROM courses")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} - {row[2]}")
    
    # Query 3: Students enrolled in IS330
    print("\n3. Students enrolled in IS330:")
    cursor.execute('''
        SELECT s.first_name, s.last_name, c.course_code
        FROM students s
        JOIN enrollments e ON s.id = e.student_id
        JOIN courses c ON e.course_id = c.id
        WHERE c.course_code = 'IS330'
    ''')
    for row in cursor.fetchall():
        print(f"   {row[0]} {row[1]} -> {row[2]}")
    
    # Query 4: Assignments for IS330
    print("\n4. Assignments for IS330:")
    cursor.execute('''
        SELECT a.title, a.due_date, a.points
        FROM assignments a
        JOIN courses c ON a.course_id = c.id
        WHERE c.course_code = 'IS330'
    ''')
    for row in cursor.fetchall():
        print(f"   {row[0]} (Due: {row[1]}, Points: {row[2]})")
    
    # Close connection
    conn.close()
    print(f"\nDatabase connection closed. File saved as: {os.path.abspath(db_name)}")

def main():
    """Main function to run the database initialization"""
    print("SQLite Database Initialization Script")
    print("=====================================")
    
    # You can change the database name here
    db_name = "course_project.db"
    
    try:
        create_database(db_name)
        print(f"\n✅ Success! Database '{db_name}' is ready to use.")
        print(f"   Location: {os.path.abspath(db_name)}")
        print("\nYou can now connect to this database from other Python scripts using:")
        print(f"   conn = sqlite3.connect('{db_name}')")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")

if __name__ == "__main__":
    main()