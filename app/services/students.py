
from flask import Flask, jsonify, request, redirect, url_for, session
from psycopg2.extras import RealDictCursor 
from datetime import timedelta
from config import db_params
import psycopg2



def student():
    if 'login_id' in session and 'roll' in session and session['roll'] == 'student':
        # User is authenticated as student
        return jsonify({'message': 'Welcome to the student portal, ' + session['username']})
    else:
        return redirect(url_for('login'))


def get_student_details():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
        
        # Retrieve stud_id from the request parameters
                stud_id = request.args.get('stud_id')

        
        if session['roll'] == 'admin':
            return jsonify({'message': 'Unauthorized'}), 401

        # Execute a SQL query to fetch student details from the database
        cur.execute('''
                SELECT
                    student.stud_name,
                    college.clg_name,
                    department.dep_name,
                    course.course_name,
                    score.score
                FROM
                    public.student
                JOIN
                    public.college ON student.clg_id = college.clg_id
                JOIN
                    public.department ON student.dep_id = department.dep_id
                JOIN
                    public.score ON student.stud_id = score.stud_id
                JOIN
                    public.course ON score.course_id = course.course_id
                WHERE
                    student.stud_id = %s;
            ''', (stud_id,))
            
        result = cur.fetchall()

        # Check if data is found and construct a JSON response
        if result:
            student_data = []
            for row in result:
                student_data.append({
                    'stud_name': row[0],
                    'clg_name': row[1],
                    'dep_name': row[2],
                    'course_name': row[3],
                    'score': row[4]
                })

            return jsonify({'student_details': student_data})
        else:
            return jsonify({'message': 'No data found'})

    except Exception as e:
        # Handle exceptions and return an error response
        return jsonify({'error': str(e)}), 500
