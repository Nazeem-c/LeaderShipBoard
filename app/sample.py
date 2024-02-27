


from flask import Flask, jsonify, request, redirect, url_for, session,Blueprint
import psycopg2
import hashlib
from psycopg2.extras import RealDictCursor 



app = Flask(__name__)
app.config['SECRET_KEY'] = 'leadershipboard'  # Replace with a secure secret key

def db_conn():
    conn = psycopg2.connect(database="LeaderShipBoard", host="localhost", user="postgres", password="postgres", port="5432")
    return conn


conn = db_conn()
cur = conn.cursor()

# -------------------------------------------------------------------admin login--------------------------------------------------------------

# @app.route('/login_admin', methods=['POST'])
# def signin():
#     data = request.get_json()
#     username = data.get('admin_id')
#     password = data.get('admin_password')
 
#     # hashed_password = hashlib.sha256(password.encode()).hexdigest()
 
#     query = "SELECT * FROM admin WHERE admin_id = %s AND admin_password = %s"
 
#     try:
#         with db_conn() as conn, conn.cursor() as cur:
#             cur.execute(query, (username, password))
#             user = cur.fetchone()
 
#         if user:
#             # For demonstration purposes, store the username in the session
#             session['username'] = username
#             return jsonify({'message': 'Sign-in successful', 'password': user[1]})
#         else:
#             return jsonify({'message': 'Invalid credentials'}), 401
 
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# ------------------------------------------------------------college------------------------------------------------------------------------


# for viewing list of every college




# update college

# delete college 

#----------------------------------------------------------------------department&Course-v1---------------------------------------------------------

# @app.route('/departments', methods=['GET'])
# def get_departments():
#     cur = conn.cursor(cursor_factory=RealDictCursor)

#     query = '''
#         SELECT d.dep_id, d.dep_name, c.c_id, c.course_name, ct.sem_no
#         FROM department d
#         LEFT JOIN contains ct ON d.dep_id = ct.dep_id
#         LEFT JOIN course c ON ct.c_id = c.c_id
#     '''

#     cur.execute(query)
#     results = cur.fetchall()

#     department_list = []
#     for result in results:
#         dep_id = result['dep_id']
#         dep_name = result['dep_name']
#         course_data = {'c_id': result['c_id'], 'course_name': result['course_name'], 'sem_no': result['sem_no']}
        
#         # Check if the department is already in the list
#         existing_department = next((dep for dep in department_list if dep['dep_id'] == dep_id), None)

#         if existing_department:
#             existing_department['courses'].append(course_data)
#         else:
#             department_data = {'dep_id': dep_id, 'dep_name': dep_name, 'courses': [course_data]}
#             department_list.append(department_data)

  

#     return jsonify({'departments': department_list})




# # Route to add data to the department table
# @app.route('/department', methods=['POST'])
# def add_department():
#     try:
#         data = request.get_json()

#         dep_name = data.get('dep_name')

#         # Insert data into the department table
#         cur.execute('''
#             INSERT INTO public.department (dep_name)
#             VALUES (%s)
#             RETURNING dep_id;
#         ''', (dep_name,))

#         dep_id = cur.fetchone()[0]
#         conn.commit()

#         return jsonify({'message': 'Department added successfully', 'dep_id': dep_id})
#     except Exception as e:
#         conn.rollback()
#         return jsonify({'error': str(e)})

# # Route to add data to the contains table
# @app.route('/contains', methods=['POST'])
# def add_contains():
#     try:
#         data = request.get_json()

#         c_id = data.get('c_id')
#         dep_id = data.get('dep_id')
#         sem_no = data.get('sem_no')

#         # Insert data into the contains table
#         cur.execute('''
#             INSERT INTO public.contains (c_id, dep_id, sem_no)
#             VALUES (%s, %s, %s)
#             RETURNING c_id;
#         ''', (c_id, dep_id, sem_no))

#         inserted_c_id = cur.fetchone()[0]
#         conn.commit()

#         return jsonify({'message': 'Contains added successfully', 'c_id': inserted_c_id})
#     except Exception as e:
#         conn.rollback()
#         return jsonify({'error': str(e)})

# # Route to add data to the course table
# @app.route('/course', methods=['POST'])
# def add_course():
#     try:
#         data = request.get_json()

#         course_name = data.get('course_name')

#         # Insert data into the course table
#         cur.execute('''
#             INSERT INTO public.course (course_name)
#             VALUES (%s)
#             RETURNING c_id;
#         ''', (course_name,))

#         inserted_c_id = cur.fetchone()[0]
#         conn.commit()

#         return jsonify({'message': 'Course added successfully', 'c_id': inserted_c_id})
#     except Exception as e:
#         conn.rollback()
#         return jsonify({'error': str(e)})
    
#------------------------------------------------------dept&course v2-----------------------------------------------------------------
#view course 
#--------------------course----------------------


#score-------------------------------------------------score--------------------- 



#score update

@app.route('/score', methods=['PUT'])
def update_score():
    try:
        conn = db_conn()
        cur = conn.cursor()
 
        # Extract data from query parameters
        course_id = request.args.get('course_id')
        stud_id = request.args.get('stud_id')
        score_value = request.args.get('score')
 
        # Update data in the score table
        cur.execute('''
            UPDATE public.score
            SET stud_id = %s, score = %s
            WHERE course_id = %s;
        ''', (stud_id, score_value, course_id))
 
        # Commit the transaction
        conn.commit()
 
        return jsonify({'message': 'Score updated successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


#delete score        
@app.route('/score', methods=['DELETE'])
def delete_score():
    course_id = request.args.get('course_id')
    return delete_score_record(course_id)

def delete_score_record(course_id):
    try:
        conn = db_conn()
        cur = conn.cursor()

        # Check whether the course with the given course_id exists
        cur.execute('SELECT * FROM public.course WHERE course_id = %s;', (course_id,))
        existing_course = cur.fetchone()

        if not existing_course:
            return jsonify({'message': f'Course with course_id {course_id} not found'}), 404

        # Delete records from the 'score' table
        cur.execute('DELETE FROM public.score WHERE course_id = %s;', (course_id,))
        conn.commit()

        return jsonify({'message': f'Records in the score table for course_id {course_id} deleted successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


#-----------------------------dept---------------------------------------------
        

# Route to add data to the department table

@app.route('/department', methods=['POST'])
def add_department():
    try:
        conn = db_conn()
        cur = conn.cursor()

        # Extract data for the department table from JSON data
        data = request.get_json()
        dep_name = data.get('dep_name')
        clg_id = request.args.get('clg_id')

        # Check if dep_name is empty or None
        if not dep_name:
            return jsonify({'error': 'Department name is required', 'message': 'Failed to add department'}), 400

        # Check if the department name already exists
        cur.execute('SELECT dep_id FROM public.department WHERE dep_name = %s', (dep_name,))
        existing_dep_id = cur.fetchone()

        if existing_dep_id:
            return jsonify({'error': 'Department with the same name already exists', 'message': 'Failed to add department'}), 400

        # Insert data into the department table
        cur.execute('''
            INSERT INTO public.department (dep_name)
            VALUES (%s)
            RETURNING dep_id;
        ''', (dep_name,))
        
        # Fetch the generated dep_id
        dep_id = cur.fetchone()[0]

        # Insert data into the college_department table
        cur.execute('''
            INSERT INTO public.college_department (clg_id, dep_id)
            VALUES (%s, %s);
        ''', (clg_id, dep_id))

        conn.commit()

        return jsonify({'message': 'Department added successfully', 'dep_id': dep_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e), 'message': 'Failed to add department'}), 500
    finally:
        cur.close()
        conn.close()

# Update department
@app.route('/department', methods=['PUT'])
def update_department():
    try:
        conn = db_conn()
        cur = conn.cursor()

        # Extract dep_id from query parameters
        dep_id = request.args.get('dep_id')

        # Validate if 'dep_name' is provided and not empty in the JSON data
        data = request.get_json()
        if 'dep_name' not in data or not data['dep_name']:
            return jsonify({'error': 'Department name (dep_name) is required and cannot be empty for updating department data'}), 400

        # Update department table
        cur.execute('''
            UPDATE public.department
            SET dep_name = %s
            WHERE dep_id = %s;
        ''', (data['dep_name'], dep_id))

        # Commit the transaction
        conn.commit()

        return jsonify({'message': 'Department data updated successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


# Sample delete operation for the department table
@app.route('/department', methods=['DELETE'])
def delete_department():
    try:
        # Extract data from query parameters
        dep_id = request.args.get('dep_id')
 
        # Delete records from college_department first
        delete_college_department_by_department(dep_id)
 
        # Now delete the department
        return delete_record('department', 'dep_id', dep_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 

# Function to delete records from college_department table by department ID
def delete_college_department_by_department(dep_id):
    try:
        conn = db_conn()
        cur = conn.cursor()
 
        # Delete from college_department table by department ID
        cur.execute('DELETE FROM public.college_department WHERE department_dep_id = %s;', (dep_id,))
        conn.commit()
 
        return jsonify({'message': f'Records in college_department referencing department {dep_id} deleted successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)})
    finally:
        cur.close()
        conn.close()
  
#-----------------------------------clg-dept----------------------------------
#Route to get data from the college_department table
@app.route('/collegedepartment', methods=['GET'])
def get_college_departments():
    try:
        conn = db_conn()
        cur = conn.cursor()
 
        # Fetch all records from college_department table
        cur.execute('SELECT * FROM public.college_department;')
        records = cur.fetchall()
 
        # Convert records to a list of dictionaries for JSON response
        result = [{'college_clg_id': record[0], 'department_dep_id': record[1]} for record in records]
 
        return jsonify({'college_departments': result})
 
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Route to add data to the college_department table
@app.route('/collegedepartment', methods=['POST'])
def add_college_department():
    try:
        data = request.get_json()
 
        college_clg_id = request.args.get('college_clg_id')
        department_dep_id = data.get('department_dep_id')
 
        # Check for duplicate entry
        cur.execute('''
            SELECT * FROM public.college_department
            WHERE college_clg_id = %s AND department_dep_id = %s;
        ''', (college_clg_id, department_dep_id))
 
        existing_entry = cur.fetchone()
 
        if existing_entry:
            return jsonify({'error': 'Duplicate entry', 'message': 'College Department already exists'}), 400
 
        # Insert data into the college_department table
        cur.execute('''
            INSERT INTO public.college_department (college_clg_id, department_dep_id)
            VALUES (%s, %s);
        ''', (college_clg_id, department_dep_id))
 
        conn.commit()
 
        return jsonify({'message': 'College Department added successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e), 'message': 'Failed to add College Department'}), 500

#--------------------------------------------------------------------------------------------------------------------------------
# Update college_department
 
#Update college_department
@app.route('/collegedepartment', methods=['PUT'])
def update_college_department():
    try:
        conn = db_conn()
        cur = conn.cursor()
 
        data = request.get_json()
 
        # Validate if 'college_clg_id' and 'department_dep_id' are provided in the JSON data
        if 'college_clg_id' not in request.args or 'department_dep_id' not in data:
            return jsonify({'error': 'College id (college_clg_id) and Department id (department_dep_id) are required for updating college_department data'}), 400
 
        college_clg_id = request.args.get('college_clg_id')
        department_dep_id = data['department_dep_id']
 
        # Update college_department table
        cur.execute('''
            UPDATE public.college_department
            SET department_dep_id = %s
            WHERE college_clg_id = %s;
        ''', (department_dep_id, college_clg_id))
 
        # Commit the transaction
        conn.commit()
 
        return jsonify({'message': 'College_department data updated successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
 
 
 
# Sample delete operation for the college_department table
@app.route('/collegedepartment', methods=['DELETE'])
def delete_college_department():
    try:
        # Extract data from query parameters
        college_clg_id = request.args.get('college_clg_id')
        department_dep_id = request.args.get('department_dep_id')
 
        # Convert values to int if needed
        college_clg_id = int(college_clg_id)
        department_dep_id = int(department_dep_id)
 
        conn = db_conn()
        cur = conn.cursor()
 
        # Delete from the college_department table
        cur.execute('''
            DELETE FROM public.college_department
            WHERE college_clg_id = %s AND department_dep_id = %s;
        ''', (college_clg_id, department_dep_id))
 
        # Commit the transaction
        conn.commit()
 
        return jsonify({'message': f'Record with college_clg_id {college_clg_id} and department_dep_id {department_dep_id} deleted successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
 

#---------------------------------semester------------------------------
# Route to add data to the semester table
@app.route('/semester', methods=['POST'])
def add_semester():
    try:
        data = request.get_json()
 
        sem_no = data.get('sem_no')
        dep_id = data.get('dep_id')
 
        # Insert data into the semester table
        cur.execute('''
            INSERT INTO public.semester (sem_no, dep_id)
            VALUES (%s, %s)
            RETURNING sem_id;
        ''', (sem_no, dep_id))
 
        sem_id = cur.fetchone()[0]
        conn.commit()
 
        return jsonify({'message': 'Semester added successfully', 'sem_id': sem_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e), 'message': 'Failed to add semester'}), 500


# Sample delete operation for the semester table
@app.route('/deletesemester', methods=['DELETE'])
def delete_semester():
    try:
        # Extract data from query parameters
        sem_id = request.args.get('sem_id')
 
        # Convert sem_id to int if needed
        sem_id = int(sem_id)
 
        conn = db_conn()
        cur = conn.cursor()
 
        # Delete from the semester table
        cur.execute('''
            DELETE FROM public.semester
            WHERE sem_id = %s;
        ''', (sem_id,))
 
        # Commit the transaction
        conn.commit()
 
        return jsonify({'message': f'Record with sem_id {sem_id} deleted successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
 
 
# Generic function for deleting records from a table
def delete_record(table_name, primary_key_name, primary_key_value):
    try:
        conn = db_conn()
        cur = conn.cursor()
 
        # Delete from the specified table
        cur.execute(f'DELETE FROM public.{table_name} WHERE {primary_key_name} = %s;', (primary_key_value,))
        conn.commit()
 
        return jsonify({'message': f'Record with {primary_key_name} {primary_key_value} deleted successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
  


#----------------------------------------------------------------------------------------------------------
# Update department


 







import re
import uuid
import random
import string

 
def generate_username(stud_name):
    unique_id = str(uuid.uuid4().hex)[:8]
    username = stud_name.lower().replace(' ', '_') + '_' + unique_id
    return username
 
def generate_password():
    password_length = 8
    password_characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(password_characters) for i in range(password_length))
    return password
 
def is_email_valid(email):
    # Email validation using a regular expression
    pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    return bool(re.match(pattern, email))
 
def is_email_unique(email):
    # Check if the email is unique in the database
    query = "SELECT COUNT(*) FROM student WHERE mail = %s"
    cur.execute(query, (email,))
    count = cur.fetchone()[0]
    return count == 0
 
@app.route('/student', methods=['POST'])
def add_student():
    if request.method == 'POST':
        try:
            data = request.get_json()
 
            # Check if required fields are present
            required_fields = ['stud_name', 'dep_id', 'batch', 'gender', 'clg_id', 'mail']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'})
 
            email = data.get('mail')
 
            # Validate email format
            if not is_email_valid(email):
                return jsonify({'error': 'Invalid email format'})
 
            # Check if the email is unique
            if not is_email_unique(email):
                return jsonify({'error': 'Email already exists!'})
 
            # Generate a simpler random password
            auto_generated_password = generate_password()
 
            # Database connection
            connection = psycopg2.connect(**db_params)
            cursor = connection.cursor()
 
            # Generate a username based on the student's name
            username = generate_username(data['stud_name'])
 
            # Insert into login table
            login_insert_query = """
            INSERT INTO login (password, username, roll)
            VALUES (%s, %s, %s)
            RETURNING login_id
            """
            cursor.execute(login_insert_query, (auto_generated_password, username, 'student'))
            login_id = cursor.fetchone()[0]
 
            # Insert into student table
            student_insert_query = """
            INSERT INTO student (stud_name, dep_id, batch, gender, clg_id, mail, login_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(student_insert_query, (
                data['stud_name'],
                data['dep_id'],
                data['batch'],
                data['gender'],
                data['clg_id'],
                email,
                login_id
            ))
 
            # Commit changes and close connection
            connection.commit()
            cursor.close()
            connection.close()
 
            return jsonify({'message': 'Student added successfully!'})
        except psycopg2.IntegrityError as e:
            # Handle specific database integrity constraint violations
            return jsonify({'error': str(e)})
        except Exception as e:
            return jsonify({'error': str(e)})
 

 #----------------------student-data-deletion

@app.route('/student/<int:stud_id>', methods=['DELETE'])
def delete_student(stud_id):
    if request.method == 'DELETE':
        try:
            # Database connection
            connection = db_conn()
            cursor = connection.cursor()
 
            # Check if student exists
            check_student_query = "SELECT * FROM student WHERE stud_id = %s"
            cursor.execute(check_student_query, (stud_id,))
            student = cursor.fetchone()
 
            if not student:
                return jsonify({'error': f'Student with ID {stud_id} not found'})
 
            # Get login_id associated with the student
            login_id_query = "SELECT login_id FROM student WHERE stud_id = %s"
            cursor.execute(login_id_query, (stud_id,))
            login_id = cursor.fetchone()[0]
 
            # Delete from student table
            delete_student_query = "DELETE FROM student WHERE stud_id = %s"
            cursor.execute(delete_student_query, (stud_id,))
 
            # Commit changes to the student table
            connection.commit()
 
            # Delete from login table using the fetched login_id
            delete_login_query = "DELETE FROM login WHERE login_id = %s"
            cursor.execute(delete_login_query, (login_id,))
 
            # Commit changes and close connection
            connection.commit()
            cursor.close()
            connection.close()
 
            return jsonify({'message': 'Student deleted successfully!'})
        except Exception as e:
            return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True,port=5002)    



