
from flask import Flask, jsonify, request, redirect, url_for, session
from psycopg2.extras import RealDictCursor 
from datetime import timedelta
from config import db_params
import psycopg2
from flask import Flask, request, jsonify
from utils.response import generate_response


from config import secret_key
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_session import Session




app = Flask(__name__)
CORS(app,supports_credentials= True) 
app.config['SESSION_TYPE'] = 'filesystem' 
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True


app.secret_key = secret_key
 # You can choose a different session type based on your needs



def student():
    if 'login_id' in session and 'roll' in session and session['roll'] == 'student':
        # User is authenticated as student
        return generate_response({'message': 'Welcome to the student portal, ' + session['username']})
    else:
        return redirect(url_for('login'))
from flask import request, session
# ... (other imports)
def get_student_details():

    try:
        # username = session.get('username')
        # Check if the user is logged in as a student
        # if 'username' in session and 'roll' in session and session['roll'] == 'student':
            # Retrieve the username from the session
           
            # username = session['username']
            username = request.args.get("username")
        # print("usr----",username)

        # Check if the user is logged in (username is in the session)
            if not username:
                return generate_response({'error': 'User not authenticated'}, 401)

            with psycopg2.connect(**db_params) as conn:
                with conn.cursor() as cur:
                    # Execute a SQL query to fetch login id based on the username
                    cur.execute('SELECT login_id FROM public.login WHERE username = %s', (username,))
                    login_id = cur.fetchone()

                    if login_id:
                        # Fetch student details using the login id
                        cur.execute('''
                            SELECT
                                student.stud_name,
                                student.stud_id,
                                department.dep_name,
                                college.clg_id,
                                college.clg_name,
                                batches.batch_id,
                                course.course_name,
                                semester.sem_no,
                                score.score
                            FROM
                                public.student
                            JOIN
                                public.score ON student.stud_id = score.stud_id
                            JOIN
                                public.course ON score.course_id = course.course_id
                            JOIN
                                public.semester ON course.sem_id = semester.sem_id
                            JOIN
                                public.batches ON student.batch = batches.batch_id
                            JOIN
                                public.college ON student.clg_id = college.clg_id
                            JOIN
                                public.department ON student.dep_id = department.dep_id
                            WHERE
                                student.login_id = %s
                            ORDER BY
                                semester.sem_no, course.course_name;
                        ''', (login_id[0],))

                        result = cur.fetchall()

                        # Check if data is found and construct a JSON response
                        if result:
                            student_name = result[0][0]
                            student_id = result[0][1]
                            dep_name = result[0][2]
                            college_id = result[0][3]
                            college_name = result[0][4]
                            batch_name = result[0][5]
                            student_details = {
                                'student_name': student_name,
                                'student_id': student_id,
                                'dep_name': dep_name,
                                'college_id': college_id,
                                'college_name': college_name,
                                'batch_name': batch_name,
                                'semesters': {},
                                'CGPA' : calculate_average_score(student_id)

                            }

                            for row in result:
                                course_name = row[6]
                                sem_no = row[7]
                                score = row[8]

                                # Create a semester entry if it doesn't exist
                                if sem_no not in student_details['semesters']:
                                    student_details['semesters'][sem_no] = {
                                        'semester_name': f'Semester {sem_no}',  # Add this line
                                        'courses': []
                                    }

                                # Add course details to the appropriate semester
                                student_details['semesters'][sem_no]['courses'].append({
                                    'course_name': course_name,
                                    'score': score
                                })

                            response = {
                                'student_details': student_details
                            }

                            return generate_response(response)
                        else:
                            return generate_response({'message': 'No data found'}, 404)
                    else:
                        return generate_response({'message': 'Login id not found for the username'}, 404)


    except Exception as e:
        # Handle exceptions and return an error response
        return generate_response({'error': str(e)}, 500)


def stud_average_score():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                if 'login_id' not in session or 'roll' not in session or session['roll'] != 'student':
                    return generate_response({'message': 'Unauthorized'},401)

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
                    return generate_response({'student': student_data})
                else:
                    return generate_response({'message': f'No data found for student with stud_id {stud_id}'}, 404)

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
                    return generate_response({'student': student_data})
                else:
                    return generate_response({'message': f'No data found for student with stud_id {stud_id}'}, 404)

    except Exception as e:
        return generate_response({'error': str(e)}, 500)


 


 #=--------------------------------------------------------------------------
def calculate_average_score(stud_id, semester_number=None):
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            if semester_number:
                # Calculate average score for the given semester
                cur.execute('''
                    SELECT AVG(a.score) AS average_score
                    FROM score a
                    JOIN course c ON a.course_id = c.course_id
                    JOIN semester s ON c.sem_id = s.sem_id
                    WHERE a.stud_id = %s AND s.sem_no = %s;
                ''', (stud_id, semester_number))
            else:
                # Calculate average score for all courses attended by the student
                cur.execute('''
                    SELECT AVG(a.score) AS average_score
                    FROM score a
                    WHERE a.stud_id = %s;
                ''', (stud_id,))
 
            average_score_result = cur.fetchone()
 
            if average_score_result:
               return round(average_score_result[0] / 10, 2)

            else:
                return None
 
 
def stud_semester_score():
    try:
        # Check if the user is logged in and is identified as a student
        username = request.args.get("username")
        # Retrieve the semester number from the request JSON data
        # data = request.get_json()
    
        semester_number = request.args.get('semester_number')
        if semester_number is None:
            return generate_response({}, 404)
        # Connect to the database
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                # Retrieve the student's ID based on the username
                cur.execute('''
                    SELECT stud_id
                    FROM student
                    JOIN login ON student.login_id = login.login_id
                    WHERE login.username = %s;
                ''', (username,))
                result = cur.fetchone()
 
                if result:
                    # Extract the student's ID from the result
                    stud_id = result[0]
 
                    # Execute the SQL query to retrieve the scores for each course in the given semester
                    cur.execute('''
                        SELECT c.course_id, c.course_name, a.score
                        FROM score a
                        JOIN course c ON a.course_id = c.course_id
                        JOIN semester s ON c.sem_id = s.sem_id
                        WHERE a.stud_id = %s AND s.sem_no = %s;
                    ''', (stud_id, semester_number))
                    score_results = cur.fetchall()
 
                    if score_results:
                        # Construct the response containing course name, id, and score
                        courses_scores = [{
                            'course_id': row[0],
                            'course_name': row[1],
                            'score': row[2]
                        } for row in score_results]
 
                        # Calculate the average score for the semester
                        average_score = calculate_average_score(stud_id, semester_number)
                        return generate_response({
                            'average_score': average_score,
                            'courses_scores': courses_scores
                        })
                    else:
                        return generate_response({'message': f'No score data found for student with username {username} in semester {semester_number}'}, 404)
                else:
                    return generate_response({'message': f'No student found with username {username}'}, 404)
 
    except Exception as e:
        return generate_response({'error': str(e)}, 500)
 
 
def stud_average_score_all():
   
        # Check if the user is logged in and is identified as a student
        username = request.args.get("username")
 
        # Connect to the database
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                # Retrieve the student's ID based on the username
                cur.execute('''
                    SELECT stud_id
                    FROM student
                    JOIN login ON student.login_id = login.login_id
                    WHERE login.username = %s;
                ''', (username,))
                result = cur.fetchone()
 
                if result:
                    # Extract the student's ID from the result
                    stud_id = result[0]
 
                    # Calculate the average score for all courses attended by the student
                    average_score = calculate_average_score(stud_id)
                    return generate_response({'average_score': average_score})
 
                else:
                    return generate_response({'message': f'No student found with username {username}'}, 404)
 
   