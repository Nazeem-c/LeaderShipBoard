from flask import Flask, jsonify, request, redirect, url_for, session
from psycopg2.extras import RealDictCursor 
from datetime import timedelta
from config import db_params
import psycopg2
from utils.response import generate_response



app = Flask(__name__)
app.config['SECRET_KEY'] = 'leadershipboard'


#1
def leaderboard():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                clg_name = request.args.get('clg_name')
                dep_name = request.args.get('dep_name')
                batch = request.args.get('batch')
                sem_no = request.args.get('sem_no')

                # Construct the base SQL query
                base_query = '''
                    SELECT
                        s.stud_id,
                        s.stud_name,
                        COALESCE(SUM(CASE WHEN %s IS NULL OR sm.sem_no <= %s THEN sc.score ELSE 0 END), 0) AS total_marks,
                        DENSE_RANK() OVER (ORDER BY COALESCE(SUM(CASE WHEN %s IS NULL OR sm.sem_no <= %s THEN sc.score ELSE 0 END), 0) DESC) AS ranking
                    FROM
                        student s
                        JOIN score sc ON s.stud_id = sc.stud_id
                        JOIN department d ON s.dep_id = d.dep_id
                        JOIN college c ON s.clg_id = c.clg_id
                        JOIN semester sm ON d.dep_id = sm.dep_id
                '''

                params = [sem_no, sem_no, sem_no, sem_no]

                # Check and append college condition
                if clg_name:
                    base_query += ' WHERE c.clg_name = %s'
                    params.append(clg_name)

                # Check and append department condition
                if dep_name:
                    if clg_name:
                        base_query += ' AND'
                    else:
                        base_query += ' WHERE'
                    base_query += ' d.dep_name = %s'
                    params.append(dep_name)

                # Check and append batch condition
                if batch:
                    if clg_name or dep_name:
                        base_query += ' AND'
                    else:
                        base_query += ' WHERE'
                    base_query += ' s.batch = %s'
                    params.append(batch)

                base_query += '''
                    GROUP BY
                        s.stud_id, s.stud_name
                    ORDER BY
                        total_marks DESC;
                '''

                cur.execute(base_query, tuple(params))
                dept_LeadershipBoard = cur.fetchall()

                if not dept_LeadershipBoard:
                    return generate_response({'error': 'No data found for the given parameters'},404)

                formatted_output = {
                    'leaderboard': [
                        {
                            'stud_id': row[0],
                            'stud_name': row[1],
                            'total_marks': row[2],
                            'ranking': row[3]
                        }
                        for row in dept_LeadershipBoard
                    ]
                }

                return generate_response(formatted_output)

    except psycopg2.Error as e:
        return generate_response({'error': f'Database error: {str(e)}'},500)
    except Exception as e:
        return generate_response({'error': str(e)},400)

#2
def college_leaderboard():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                dep_name = request.args.get('dep_name')
                batch = request.args.get('batch')

                # Construct the base SQL query
                base_query = '''
                    SELECT
                        c.clg_name,
                        AVG(CASE WHEN %s IS NULL OR s.dep_id = d.dep_id THEN sc.score ELSE 0 END) AS average_score,
                        AVG(CASE WHEN %s IS NULL OR s.dep_id = d.dep_id THEN CASE WHEN sc.score >= 40 THEN 1 ELSE 0 END ELSE 0 END) * 100 AS pass_percentage
                    FROM
                        college c
                        JOIN student s ON c.clg_id = s.clg_id
                        JOIN department d ON s.dep_id = d.dep_id
                        LEFT JOIN score sc ON s.stud_id = sc.stud_id
                '''

                params = [dep_name, dep_name]

                # Check and append batch condition
                if batch:
                    base_query += ' WHERE s.batch = %s'
                    params.append(batch)

                base_query += '''
                    GROUP BY
                        c.clg_name
                    ORDER BY
                        pass_percentage DESC;
                '''

                cur.execute(base_query, tuple(params))
                college_LeadershipBoard = cur.fetchall()

                if not college_LeadershipBoard:
                    return generate_response({'error': 'No data found for the given parameters'},404)

                formatted_output = {
                    'leaderboard': [
                        {
                            'clg_name': row[0],
                            'average_score': row[1],
                            'pass_percentage': row[2]
                        }
                        for row in college_LeadershipBoard
                    ]
                }

                return generate_response(formatted_output)

    except psycopg2.Error as e:
        return generate_response({'error': f'Database error: {str(e)}'},500)
    except Exception as e:
        return generate_response({'error': str(e)},400)

#3

def department_leaderboard():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                clg_name = request.args.get('clg_name')
                batch = request.args.get('batch')

                # Construct the base SQL query
                base_query = '''
                    SELECT
                        d.dep_name,
                        AVG(CASE WHEN %s IS NULL OR s.clg_id = c.clg_id THEN sc.score ELSE 0 END) AS average_score,
                        AVG(CASE WHEN %s IS NULL OR s.clg_id = c.clg_id THEN CASE WHEN sc.score >= 40 THEN 1 ELSE 0 END ELSE 0 END) * 100 AS pass_percentage
                    FROM
                        department d
                        JOIN student s ON d.dep_id = s.dep_id
                        LEFT JOIN score sc ON s.stud_id = sc.stud_id
                        LEFT JOIN college c ON s.clg_id = c.clg_id
                '''

                params = [clg_name, clg_name]

                # Check and append batch condition
                if batch:
                    base_query += ' WHERE s.batch = %s'
                    params.append(batch)

                base_query += '''
                    GROUP BY
                        d.dep_name
                    ORDER BY
                        pass_percentage DESC;
                '''

                cur.execute(base_query, tuple(params))
                dept_LeadershipBoard = cur.fetchall()

                if not dept_LeadershipBoard:
                    return generate_response({'error': 'No data found for the given parameters'},404)

                formatted_output = {
                    'leaderboard': [
                        {
                            'dep_name': row[0],
                            'average_score': row[1],
                            'pass_percentage': row[2]
                        }
                        for row in dept_LeadershipBoard
                    ]
                }

                return generate_response(formatted_output)

    except psycopg2.Error as e:
        return generate_response({'error': f'Database error: {str(e)}'},500)
    except Exception as e:
        return generate_response({'error': str(e)},400)




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
                    SELECT s.stud_id, s.stud_name, SUM(sc.score) AS total_marks
                    FROM student s
                    JOIN score sc ON s.stud_id = sc.stud_id
                    WHERE s.batch = %s
                    GROUP BY s.stud_id, s.stud_name
                    ORDER BY total_marks DESC;
                ''', (batch,))

                batch_LeadershipBoard = cur.fetchall()

                # Add ranking to the result
                ranked_data = []
                rank = 1
                for row in batch_LeadershipBoard:
                    stud_id, stud_name, total_marks = row
                    ranked_data.append({
                        'rank': rank,
                        'stud_id': stud_id,
                        'stud_name': stud_name,
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
                        SUM(sc.score) AS total_marks,
                        RANK() OVER (ORDER BY SUM(sc.score) DESC) AS ranking
                    FROM
                        student s
                        JOIN score sc ON s.stud_id = sc.stud_id
                        JOIN department d ON s.dep_id = d.dep_id
                    WHERE
                        d.dep_name = %s AND s.batch = %s
                    GROUP BY
                        s.stud_id, s.stud_name
                    ORDER BY
                        total_marks DESC;
                ''', (department, batch))

                dept_LeadershipBoard = cur.fetchall()

                result = {'LeadershipBoard_dept_batch': []}

                for row in dept_LeadershipBoard:
                    student_info = {
                        'stud_id': row[0],
                        'stud_name': row[1],
                        'total_marks': row[2],
                        'ranking': row[3]
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

                if not clg_name:
                    return jsonify({'error': 'clg_name is required'}), 400

                cur.execute('''
                    SELECT
                        s.stud_id,
                        s.stud_name,
                        SUM(sc.score) AS total_marks
                    FROM
                        student s
                        JOIN score sc ON s.stud_id = sc.stud_id
                        JOIN department d ON s.dep_id = d.dep_id
                        JOIN college c ON s.clg_id = c.clg_id
                    WHERE
                        c.clg_name = %s
                    GROUP BY
                        s.stud_id, s.stud_name
                    ORDER BY
                        total_marks DESC;
                ''', (clg_name,))

                dept_LeadershipBoard = cur.fetchall()
                formatted_output = []

                rank = 1
                prev_marks = None

                for row in dept_LeadershipBoard:
                    current_marks = row[2]

                    student_info = {
                        'stud_id': row[0],
                        'stud_name': row[1],
                        'total_marks': current_marks,
                        'ranking': rank
                    }
                    formatted_output.append(student_info)

                    if prev_marks is not None and current_marks != prev_marks:
                        rank += 1

                    prev_marks = current_marks

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


# def leaderboard():
#     try:
#         with psycopg2.connect(**db_params) as conn:
#             with conn.cursor() as cur:
#                 clg_name = request.args.get('clg_name')
#                 dep_name = request.args.get('dep_name')
#                 batch = request.args.get('batch')
#                 sem_no = request.args.get('sem_no')

#                 # Construct the base SQL query
#                 base_query = '''
#                     SELECT
#                         s.stud_id,
#                         s.stud_name,
#                         COALESCE(SUM(CASE WHEN %s IS NULL OR sm.sem_no <= %s THEN sc.score ELSE 0 END), 0) AS total_marks,
#                         DENSE_RANK() OVER (ORDER BY COALESCE(SUM(CASE WHEN %s IS NULL OR sm.sem_no <= %s THEN sc.score ELSE 0 END), 0) DESC) AS ranking
#                     FROM
#                         student s
#                         JOIN score sc ON s.stud_id = sc.stud_id
#                         JOIN department d ON s.dep_id = d.dep_id
#                         JOIN college c ON s.clg_id = c.clg_id
#                         JOIN semester sm ON d.dep_id = sm.dep_id
#                 '''

#                 params = [sem_no, sem_no, sem_no, sem_no]

#                 # Check and append college condition
#                 if clg_name:
#                     base_query += ' WHERE c.clg_name = %s'
#                     params.append(clg_name)

#                 # Check and append department condition
#                 if dep_name:
#                     if clg_name:
#                         base_query += ' AND'
#                     else:
#                         base_query += ' WHERE'
#                     base_query += ' d.dep_name = %s'
#                     params.append(dep_name)

#                 # Check and append batch condition
#                 if batch:
#                     if clg_name or dep_name:
#                         base_query += ' AND'
#                     else:
#                         base_query += ' WHERE'
#                     base_query += ' s.batch = %s'
#                     params.append(batch)

#                 base_query += '''
#                     GROUP BY
#                         s.stud_id, s.stud_name
#                     ORDER BY
#                         total_marks DESC;
#                 '''

#                 cur.execute(base_query, tuple(params))
#                 dept_LeadershipBoard = cur.fetchall()

#                 if not dept_LeadershipBoard:
#                     return jsonify({'error': 'No data found for the given parameters'}), 404

#                 formatted_output = {
#                     'leaderboard': [
#                         {
#                             'stud_id': row[0],
#                             'stud_name': row[1],
#                             'total_marks': row[2],
#                             'ranking': row[3]
#                         }
#                         for row in dept_LeadershipBoard
#                     ]
#                 }

#                 return jsonify(formatted_output)

#     except psycopg2.Error as e:
#         return jsonify({'error': f'Database error: {str(e)}'}), 500
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

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


def list_colleges():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                # Construct the SQL query to calculate average score and pass percentage for each college
                sql_query = '''
                    SELECT
                        c.clg_id,
                        c.clg_name,
                        AVG(sc.score) AS average_score,
                        AVG(CASE WHEN sc.score >= 40 THEN 1 ELSE 0 END) * 100 AS pass_percentage
                    FROM
                        college c
                        LEFT JOIN student s ON c.clg_id = s.clg_id
                        LEFT JOIN score sc ON s.stud_id = sc.stud_id
                    GROUP BY
                        c.clg_id, c.clg_name
                '''

                cur.execute(sql_query)
                college_data = cur.fetchall()

                # Calculate college rank based on a combination of average score and pass percentage
                ranked_colleges = []
                for idx, college in enumerate(sorted(college_data, key=lambda x: (x[2] or Decimal(0), x[3] or Decimal(0)), reverse=True), start=1):
                    clg_id, clg_name, average_score, pass_percentage = college
                    rank = idx

                    ranked_colleges.append({
                        'rank': rank,
                        'college_details': {
                            'clg_id': clg_id,
                            'clg_name': clg_name,
                            'average_score': average_score,
                            'pass_percentage': min(pass_percentage or Decimal(0), 100)  # Ensure pass percentage is within 100
                        }
                    })

        return jsonify({'ranked_colleges': ranked_colleges})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_college_info():
    try:
        # Get college_name from the request parameters
        college_name = request.args.get('clg_name')

        if not college_name:
            return jsonify({'error': 'College name parameter is required'})

        # Database connection
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cursor:
                # Get college_id for the given college_name
                cursor.execute("SELECT clg_id FROM public.college WHERE clg_name = %s", (college_name,))
                college_id = cursor.fetchone()

                if not college_id:
                    return jsonify({'error': f'College with name {college_name} not found'})

                college_id = college_id[0]

                # Get department details for the specified college
                cursor.execute("SELECT dep_id, dep_name FROM public.department WHERE dep_id IN (SELECT department_dep_id FROM public.college_department WHERE college_clg_id = %s)", (college_id,))
                departments = cursor.fetchall()

                college_info = {'college_name': college_name, 'departments': []}

                for dep_id, dep_name in departments:
                    department_info = {'dep_id': dep_id, 'dep_name': dep_name, 'batches': []}

                    # Get batch-wise student details for the department
                    cursor.execute("SELECT DISTINCT batch FROM public.student WHERE dep_id = %s", (dep_id,))
                    batches = cursor.fetchall()

                    for batch in batches:
                        batch_info = {'batch': batch[0], 'students': []}

                        # Get student details for the batch
                        cursor.execute("""
                            SELECT s.stud_id, s.stud_name
                            FROM public.student s
                            WHERE s.dep_id = %s AND s.batch = %s
                        """, (dep_id, batch[0]))
                        students = cursor.fetchall()

                        student_scores = []  # List to store tuples (total_score, stud_id, student_info) for sorting
                        for stud_id, stud_name in students:
                            student_info = {
                                'stud_id': stud_id,
                                'stud_name': stud_name,
                                'total_score': 0  # Initialize total score
                            }

                            # Get total score for the student
                            cursor.execute("""
                                SELECT COALESCE(SUM(score), 0)
                                FROM public.score
                                WHERE stud_id = %s
                            """, (stud_id,))
                            total_score = cursor.fetchone()[0]
                            student_info['total_score'] = total_score

                            student_scores.append((total_score, stud_id, student_info))

                        # Sort students based on total score and stud_id in descending order
                        student_scores.sort(key=lambda x: (x[0], -x[1]), reverse=True)
                        rank = 0
                        prev_total_score = float('inf')

                        for total_score, stud_id, student_info in student_scores:
                            if total_score < prev_total_score:
                                rank += 1
                            student_info['rank'] = rank
                            prev_total_score = total_score
                            batch_info['students'].append(student_info)

                        department_info['batches'].append(batch_info)

                    college_info['departments'].append(department_info)

        # Return the college_info
        return jsonify(college_info)

    except Exception as e:
        return jsonify({'error': str(e)})


def get_students_details_dept():
    try:
        # Extract department name from query parameters
        department_name = request.args.get('dept_name')

        if not department_name:
            return jsonify({'error': 'Department name parameter is required'}), 400

        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cursor:
                # Construct the SQL query with department and college information
                sql_query = '''
                    SELECT
                        cl.clg_name as college_name,
                        s.stud_id,
                        s.stud_name,
                        s.batch,
                        COALESCE(SUM(sc.score), 0) AS total_score
                    FROM
                        student s
                        JOIN department d ON s.dep_id = d.dep_id
                        JOIN college cl ON s.clg_id = cl.clg_id  -- Adjust based on your actual relationship
                        LEFT JOIN score sc ON s.stud_id = sc.stud_id
                    WHERE
                        d.dep_name = %s
                    GROUP BY
                        cl.clg_name, s.stud_id, s.stud_name, s.batch
                    ORDER BY
                        s.batch, total_score DESC, s.stud_id;
                '''

                cursor.execute(sql_query, (department_name,))
                student_data = cursor.fetchall()

                # Organize data into the desired structure
                departments_with_batches = {}
                current_batch = None
                current_student = None
                current_rank = 0
                previous_total_score = None

                for row in student_data:
                    college_name, stud_id, stud_name, batch, total_score = row

                    if batch not in departments_with_batches:
                        departments_with_batches[batch] = {
                            'students': []
                        }

                    # Start a new student record within the batch
                    current_student = {
                        'college_name': college_name,
                        'stud_id': stud_id,
                        'stud_name': stud_name,
                        'total_score': total_score,
                        'rank': 0  # Rank will be assigned later
                    }
                    departments_with_batches[batch]['students'].append(current_student)

                    # Assign ranks based on the total score within each batch
                    if total_score == previous_total_score:
                        current_student['rank'] = current_rank
                    else:
                        current_rank += 1
                        current_student['rank'] = current_rank

                    previous_total_score = total_score

        return jsonify(departments_with_batches)

    except Exception as e:
        return jsonify({'error': f'Something went wrong: {str(e)}'}), 500
