from flask import Flask, jsonify, request, redirect, url_for, session
from psycopg2.extras import RealDictCursor 
from datetime import timedelta
from config import db_params
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'leadershipboard'


def get_topper():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT s.stud_id, s.stud_name, SUM(sc.score) AS total_marks
                    FROM student s
                    JOIN score sc ON s.stud_id = sc.stud_id
                    GROUP BY s.stud_id, s.stud_name
                    ORDER BY total_marks DESC;
                ''')

                College_LeadershipBoard = cur.fetchall()

                # Assign ranks based on the total_marks
                ranked_board = [
                    {
                        'stud_id': stud_id,
                        'stud_name': stud_name,
                        'total_marks': total_marks,
                        'rank': idx + 1
                    }
                    for idx, (stud_id, stud_name, total_marks) in enumerate(College_LeadershipBoard)
                ]

                return jsonify({'LeadershipBoard': ranked_board})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_topper_batch():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                # Retrieve batch from query parameter
                batch = request.args.get('batch')

                # Check if batch is provided
                if not batch:
                    return jsonify({'error': 'Batch parameter is required'}), 400

                cur.execute('''
                    SELECT s.stud_id, s.stud_name, s.batch, SUM(sc.score) AS total_marks
                    FROM student s
                    JOIN score sc ON s.stud_id = sc.stud_id
                    WHERE s.batch = %s
                    GROUP BY s.stud_id, s.stud_name, s.batch
                    ORDER BY total_marks DESC;
                ''', (batch,))

                batch_LeadershipBoard = cur.fetchall()

                # Add ranking to the result
                ranked_data = []
                rank = 1
                for row in batch_LeadershipBoard:
                    stud_id, stud_name, student_batch, total_marks = row
                    ranked_data.append({
                        'rank': rank,
                        'stud_id': stud_id,
                        'stud_name': stud_name,
                        'batch': student_batch,
                        'total_marks': total_marks
                    })
                    rank += 1

                return jsonify({'LeadershipBoard_batch': ranked_data})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_topper_dept():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                dep_name = request.args.get('department')

                cur.execute('''
                    SELECT
                        s.stud_id,
                        s.stud_name,
                        SUM(a.score) AS total_score,
                        RANK() OVER (ORDER BY SUM(a.score) DESC) AS ranking
                    FROM
                        student s
                        JOIN score a ON s.stud_id = a.stud_id
                        JOIN department d ON s.dep_id = d.dep_id
                    WHERE
                        d.dep_name = %s
                    GROUP BY
                        s.stud_id, s.stud_name
                    ORDER BY
                        total_score DESC;
                ''', (dep_name,))

                dept_LeadershipBoard = cur.fetchall()

                # Transforming result to key-value pairs
                formatted_result = []
                for row in dept_LeadershipBoard:
                    student_info = {
                        'stud_id': row[0],
                        'stud_name': row[1],
                        'total_score': row[2],
                        'ranking': row[3]
                    }
                    formatted_result.append(student_info)

                return jsonify({'LeadershipBoard_department': formatted_result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_topper_dept_batch():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                department = request.args.get('department')
                batch = request.args.get('batch')

                cur.execute('''
                    SELECT
                        s.stud_id,
                        s.stud_name,
                        d.dep_name,
                        s.batch,
                        SUM(sc.score) AS total_marks,
                        RANK() OVER (ORDER BY SUM(sc.score) DESC) AS ranking
                    FROM
                        student s
                        JOIN score sc ON s.stud_id = sc.stud_id
                        JOIN department d ON s.dep_id = d.dep_id
                    WHERE
                        d.dep_name = %s AND s.batch = %s
                    GROUP BY
                        s.stud_id, s.stud_name, d.dep_name, s.batch
                    ORDER BY
                        total_marks DESC;
                ''', (department, batch))

                dept_LeadershipBoard = cur.fetchall()

                result = {'LeadershipBoard_dept_batch': []}

                for row in dept_LeadershipBoard:
                    student_info = {
                        'stud_id': row[0],
                        'stud_name': row[1],
                        'dep_name': row[2],
                        'batch': row[3],
                        'total_marks': row[4],
                        'ranking': row[5]
                    }
                    result['LeadershipBoard_dept_batch'].append(student_info)

                return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_topper_college_dept():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                clg_name = request.args.get('clg_name')
                dep_name = request.args.get('dep_name')

                if not clg_name or not dep_name:
                    return jsonify({'error': 'Both clg_name and dep_name are required'}), 400

                cur.execute('''
                    SELECT
                        s.stud_id,
                        s.stud_name,
                        d.dep_name,
                        SUM(sc.score) AS total_marks,
                        RANK() OVER (ORDER BY SUM(sc.score) DESC) AS ranking
                    FROM
                        student s
                        JOIN score sc ON s.stud_id = sc.stud_id
                        JOIN department d ON s.dep_id = d.dep_id
                        JOIN college c ON s.clg_id = c.clg_id
                    WHERE
                        c.clg_name = %s AND d.dep_name = %s
                    GROUP BY
                        s.stud_id, s.stud_name, d.dep_name
                    ORDER BY
                        total_marks DESC;
                ''', (clg_name, dep_name))

                dept_LeadershipBoard = cur.fetchall()
                formatted_output = []

                for row in dept_LeadershipBoard:
                    student_info = {
                        'stud_id': row[0],
                        'stud_name': row[1],
                        'dep_name': row[2],
                        'total_marks': row[3],
                        'ranking': row[4]
                    }
                    formatted_output.append(student_info)

                return jsonify({'LeadershipBoard_college_dept': formatted_output})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_topper_college_dept_batch():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                clg_name = request.args.get('clg_name')
                dep_name = request.args.get('dep_name')
                batch = request.args.get('batch')

                cur.execute('''
                    SELECT
                        s.stud_id,
                        s.stud_name,
                        d.dep_name,
                        s.batch,
                        SUM(sc.score) AS total_marks,
                        RANK() OVER (ORDER BY SUM(sc.score) DESC) AS ranking
                    FROM
                        student s
                        JOIN score sc ON s.stud_id = sc.stud_id
                        JOIN department d ON s.dep_id = d.dep_id
                        JOIN college c ON s.clg_id = c.clg_id
                    WHERE
                        c.clg_name = %s AND d.dep_name = %s AND s.batch = %s
                    GROUP BY
                        s.stud_id, s.stud_name, d.dep_name, s.batch
                    ORDER BY
                        total_marks DESC;
                ''', (clg_name, dep_name, batch))

                dept_LeadershipBoard = cur.fetchall()

                formatted_output = {
                    'college_name': clg_name,
                    'department_name': dep_name,
                    'batch': batch,
                    'toppers': [
                        {
                            'stud_id': row[0],
                            'stud_name': row[1],
                            'department_name': row[2],
                            'batch': row[3],
                            'total_marks': row[4],
                            'ranking': row[5]
                        }
                        for row in dept_LeadershipBoard
                    ]
                }

                return jsonify({'LeadershipBoard_college_dept_batch': formatted_output})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_all_students():
    try:
        # Extract department_id and batch from query parameters
        department_id = request.args.get('dep_id')
        batch = request.args.get('batch')

        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                # Construct the SQL query with optional department and batch filtering
                sql_query = '''
                    SELECT
                        s.stud_id,
                        s.stud_name,
                        s.batch,
                        s.dep_id,
                        d.dep_name,
                        c.course_id,
                        c.course_name,
                        COALESCE(sc.score, 0) AS score
                    FROM
                        student s
                        JOIN department d ON s.dep_id = d.dep_id
                        CROSS JOIN course c
                        LEFT JOIN score sc ON s.stud_id = sc.stud_id AND c.course_id = sc.course_id
                '''

                filters = []

                if department_id:
                    filters.append(f"s.dep_id = {department_id}")

                if batch:
                    filters.append(f"s.batch = '{batch}'")

                if filters:
                    sql_query += " WHERE " + " AND ".join(filters)

                sql_query += " ORDER BY s.batch, s.dep_id, s.stud_id, c.course_id;"

                cur.execute(sql_query)
                student_data = cur.fetchall()

                # Organize data into the desired nested structure
                students_with_scores = []
                current_batch = None
                current_department = None
                current_student = None

                for row in student_data:
                    stud_id, stud_name, student_batch, student_department, department_name, course_id, course_name, score = row

                    if current_batch is None or current_batch['batch'] != student_batch:
                        # Start a new batch record
                        current_batch = {
                            'batch': student_batch,
                            'departments': []
                        }
                        students_with_scores.append(current_batch)

                    if current_department is None or current_department['dep_id'] != student_department:
                        # Start a new department record within the batch
                        current_department = {
                            'dep_id': student_department,
                            'dep_name': department_name,
                            'students': []
                        }
                        current_batch['departments'].append(current_department)

                    if current_student is None or current_student['stud_id'] != stud_id:
                        # Start a new student record within the department
                        current_student = {
                            'stud_id': stud_id,
                            'stud_name': stud_name,
                            'scores': [],
                            'sum_of_scores': 0  # Initialize sum_of_scores
                        }
                        current_department['students'].append(current_student)

                    # Add score details to the current student record
                    current_student['scores'].append({
                        'course_id': course_id,
                        'course_name': course_name,
                        'score': score
                    })

                    # Update the sum_of_scores
                    current_student['sum_of_scores'] += score

                # Assign ranks based on the total score
                for batch in students_with_scores:
                    for department in batch['departments']:
                        department['students'] = sorted(department['students'], key=lambda x: x['sum_of_scores'], reverse=True)
                        for idx, student in enumerate(department['students']):
                            student['rank'] = idx + 1

                # Transform the structure for better readability
                formatted_students = [
                    {
                        'batch': batch['batch'],
                        'departments': [
                            {
                                'dep_id': department['dep_id'],
                                'dep_name': department['dep_name'],
                                'students': [
                                    {
                                        'stud_id': student['stud_id'],
                                        'stud_name': student['stud_name'],
                                        'scores': student['scores'],
                                        'sum_of_scores': student['sum_of_scores'],
                                        'rank': student['rank']
                                    }
                                    for student in department['students']
                                ]
                            }
                            for department in batch['departments']
                        ]
                    }
                    for batch in students_with_scores
                ]

                return jsonify(students=formatted_students)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_students_details():
    try:
        # Extract batch from query parameters
        batch = request.args.get('batch')
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                if not batch:
                    return jsonify({'error': 'Batch parameter is required'}), 400

                # Construct the SQL query with batch filtering
                sql_query = '''
                    SELECT
                        s.stud_id,
                        s.stud_name,
                        s.dep_id,
                        d.dep_name,
                        c.course_id,
                        c.course_name,
                        COALESCE(sc.score, 0) AS score
                    FROM
                        student s
                        JOIN department d ON s.dep_id = d.dep_id
                        CROSS JOIN course c
                        LEFT JOIN score sc ON s.stud_id = sc.stud_id AND c.course_id = sc.course_id
                    WHERE
                        s.batch = %s
                    ORDER BY s.stud_id, c.course_id;
                '''

                cur.execute(sql_query, (batch,))
                student_data = cur.fetchall()

                # Organize data into the desired nested structure
                students_with_details = []
                current_student = None

                for row in student_data:
                    stud_id, stud_name, student_department, department_name, course_id, course_name, score = row

                    if current_student is None or current_student['stud_id'] != stud_id:
                        # Start a new student record
                        current_student = {
                            'stud_id': stud_id,
                            'stud_name': stud_name,
                            'dep_id': student_department,
                            'dep_name': department_name,
                            'scores': [],
                            'total_score': 0  # Initialize total_score
                        }
                        students_with_details.append(current_student)

                    # Add score details to the current student record
                    current_student['scores'].append({
                        'course_id': course_id,
                        'course_name': course_name,
                        'score': score
                    })

                    # Update the total_score
                    current_student['total_score'] += score

                return jsonify(students=students_with_details)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_leadership_board():
    # Get the batch and semester number from the query parameters
    batch = request.args.get('batch')
    sem_no = request.args.get('sem_no')

    # Check if both batch and semester number are provided
    if not batch or not sem_no:
        return jsonify({'error': 'Both batch and semester number are required in the query parameters'}), 400

    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                # Get the leadership board based on batch and semester number
                get_leadership_board_query = """
                SELECT
                    s.stud_id,
                    s.stud_name,
                    d.dep_name,
                    s.batch,
                    s.gender,
                    s.clg_id,
                    s.mail,
                    COALESCE(SUM(sc.score), 0) AS total_score,
                    RANK() OVER (ORDER BY COALESCE(SUM(sc.score), 0) DESC NULLS LAST) AS rank
                FROM
                    student s
                    LEFT JOIN score sc ON s.stud_id = sc.stud_id
                    LEFT JOIN course c ON sc.course_id = c.course_id
                    JOIN department d ON s.dep_id = d.dep_id
                    JOIN semester sm ON c.sem_id = sm.sem_id
                WHERE
                    s.batch = %s AND sm.sem_no = %s
                GROUP BY
                    s.stud_id, s.stud_name, d.dep_name, s.batch, s.gender, s.clg_id, s.mail
                ORDER BY
                    rank DESC NULLS LAST;
                """
                cur.execute(get_leadership_board_query, (batch, sem_no))
                leadership_board = cur.fetchall()

        if not leadership_board:
            return jsonify({'message': f'No data found for the given batch and semester number'}), 404

        # Construct the response
        response = {f'stud_id_{student[0]}': {
            'stud_name': student[1],
            'dep_name': student[2],
            'total_score': student[7],
            'rank': student[8],
            'courses': fetch_courses_for_student(student[0], sem_no)
        } for student in leadership_board}

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
def fetch_courses_for_student(stud_id, sem_no):
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                get_courses_query = """
                    SELECT c.course_name, sc.score
                    FROM student s
                    LEFT JOIN score sc ON s.stud_id = sc.stud_id
                    LEFT JOIN course c ON sc.course_id = c.course_id
                    JOIN semester sm ON c.sem_id = sm.sem_id
                    WHERE s.stud_id = %s AND sm.sem_no = %s;
                """
                cur.execute(get_courses_query, (stud_id, sem_no))
                courses = cur.fetchall()

                formatted_courses = [
                    {'course_name': course[0], 'score': course[1]} if len(course) > 1 else {'course_name': course[0], 'score': None} for course in courses
                ]

                return formatted_courses

    except Exception as e:
        return [{'error': str(e)}]
