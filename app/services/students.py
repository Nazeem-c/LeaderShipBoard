
from flask import Flask, jsonify, request, redirect, url_for, session
from psycopg2.extras import RealDictCursor 
from datetime import timedelta
from config import db_params
import psycopg2
from flask import Flask, request, jsonify


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

                if 'login_id' not in session or 'roll' not in session or session['roll'] != 'student':
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
                    student_details = {
                        'stud_name': result[0][0],
                        'college': {
                            'clg_name': result[0][1],
                            'department': {
                                'dep_name': result[0][2]
                            }
                        },
                        'courses': []
                    }

                    for row in result:
                        student_details['courses'].append({
                            'course_name': row[3],
                            'score': row[4]
                        })

                    return jsonify({'student_details': student_details})
                else:
                    return jsonify({'message': 'No data found'})

    except Exception as e:
        # Handle exceptions and return an error response
        return jsonify({'error': str(e)}), 500


def stud_average_score():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                if 'login_id' not in session or 'roll' not in session or session['roll'] != 'student':
                    return jsonify({'message': 'Unauthorized'}), 401

                # Get stud_id from the query parameters
                stud_id = request.args.get('stud_id')

                # If stud_id is not provided, use the one from the session
                if not stud_id:
                    stud_id = session.get('stud_id')

                cur.execute('''
                    SELECT s.stud_id, s.stud_name, AVG(a.score) AS average_score
                    FROM student s
                    JOIN score a ON s.stud_id = a.stud_id
                    WHERE s.stud_id = %s
                    GROUP BY s.stud_id, s.stud_name;
                ''', (stud_id,))
                
                results = cur.fetchall()

                if results:
                    student_data = {
                        'stud_id': results[0][0],
                        'stud_name': results[0][1],
                        'average_score': results[0][2]
                    }
                    return jsonify({'student': student_data})
                else:
                    return jsonify({'message': f'No data found for student with stud_id {stud_id}'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_current_semester():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                if 'login_id' not in session or 'roll' not in session or session['roll'] != 'student':
                    return jsonify({'message': 'Unauthorized'}), 401

                # Get stud_id from the query parameters
                stud_id = request.args.get('stud_id')

                # If stud_id is not provided, use the one from the session
                if not stud_id:
                    stud_id = session.get('stud_id')

                cur.execute('''
                    SELECT MAX(s.sem_no) AS current_semester
                    FROM student st
                    JOIN department d ON st.dep_id = d.dep_id
                    JOIN semester s ON d.dep_id = s.dep_id
                    WHERE st.stud_id = %s;
                ''', (stud_id,))

                results = cur.fetchall()

                if results:
                    student_data = {
                        'stud_id': stud_id,
                        'current_semester': results[0][0] if len(results[0]) > 0 else None
                    }
                    return jsonify({'student': student_data})
                else:
                    return jsonify({'message': f'No data found for student with stud_id {stud_id}'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


 