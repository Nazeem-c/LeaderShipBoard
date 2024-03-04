from flask import Flask, jsonify, request, redirect, url_for, session
from psycopg2.extras import RealDictCursor 
from datetime import timedelta
from config import db_params
import psycopg2
from utils.usnamepaswrdgnrtn import *
from utils.mailscore import *
from utils.response import generate_response

from config import secret_key



app = Flask(__name__)
app.secret_key = secret_key



def admin():
    if 'login_id' in session and 'roll' in session and session['roll'] == 'admin':
        # User is authenticated as admin
        return generate_response({'message': 'Welcome to the admin portal, ' + session['username']})
    else:
        return generate_response(url_for('login'))

def get_college():
    query = """
        SELECT c.clg_id, c.clg_name, c.contact, c.established_year, a.place, a.state, a.pin
        FROM college c
        JOIN address a ON c.addr_id = a.addr_id
    """

    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                if 'login_id' not in session or 'roll' not in session or session['roll'] != 'admin':
                    return jsonify({'message': 'Unauthorized'}), 401
                cur.execute(query)
                results = cur.fetchall()

                colleges = []

                for result in results:
                    clg_id, clg_name, contact, established_year, place, state, pin = result

                    college_info = {
                        'clg_id': clg_id,
                        'clg_name': clg_name,
                        'contact': contact,
                        'established_year': established_year,
                        'place': place,
                        'state': state,
                        'pin': pin
                    }

                    colleges.append(college_info)

        return jsonify({'colleges': colleges})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def add_college():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                if 'login_id' not in session or 'roll' not in session or session['roll'] != 'admin':
                    return jsonify({'message': 'Unauthorized'}), 401
                data = request.get_json()

                clg_name = data['clg_name']
                contact = data['contact']
                established_year = data['established_year']
                place = data['place']
                state = data['state']
                pin = data['pin']

                query_check_duplicate = "SELECT clg_id FROM college WHERE clg_name = %s"

                cur.execute(query_check_duplicate, (clg_name,))
                existing_clg_id = cur.fetchone()

                if existing_clg_id:
                    return jsonify({'message': 'College with the same name already exists'}), 400

                query_address = "INSERT INTO address (place, state, pin) VALUES (%s, %s, %s) RETURNING addr_id"

                cur.execute(query_address, (place, state, pin))
                addr_id = cur.fetchone()[0]

                query_college = "INSERT INTO college (clg_name, contact, established_year, addr_id) VALUES (%s, %s, %s, %s)"

                cur.execute(query_college, (clg_name, contact, established_year, addr_id))
                conn.commit()

        return jsonify({'message': 'College added successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def update_college():
    try:
        if 'login_id' not in session or 'roll' not in session or session['roll'] != 'admin':
                    return jsonify({'message': 'Unauthorized'}), 401
        clg_id = request.args.get('clg_id')
        
        if clg_id is None:
            return jsonify({'error': 'clg_id is required in the query parameters'}), 400
        
        clg_id = int(clg_id)  # Convert clg_id to integer

        data = request.get_json()
        clg_name = data.get('clg_name')
        contact = data.get('contact')
        established_year = data.get('established_year')
        place = data.get('place')
        state = data.get('state')
        pin = data.get('pin')

        query_check_existence = "SELECT clg_id FROM college WHERE clg_id = %s"
        
        with psycopg2.connect(**db_params) as conn, conn.cursor() as cur:
            cur.execute(query_check_existence, (clg_id,))
            existing_clg_id = cur.fetchone()

            if not existing_clg_id:
                return jsonify({'message': f'College not found for clg_id {clg_id}'}), 404

        query_update_address = "UPDATE address SET place = %s, state = %s, pin = %s WHERE addr_id = (SELECT addr_id FROM college WHERE clg_id = %s)"

        with psycopg2.connect(**db_params) as conn, conn.cursor() as cur:
            cur.execute(query_update_address, (place, state, pin, clg_id))

        query_update_college = "UPDATE college SET clg_name = %s, contact = %s, established_year = %s WHERE clg_id = %s"

        with psycopg2.connect(**db_params) as conn, conn.cursor() as cur:
            cur.execute(query_update_college, (clg_name, contact, established_year, clg_id))
            conn.commit()

        return jsonify({'message': f'College with clg_id {clg_id} updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def delete_college():
    try:
        if 'login_id' not in session or 'roll' not in session or session['roll'] != 'admin':
                    return jsonify({'message': 'Unauthorized'}), 401
        clg_id = request.args.get('clg_id')

        if not clg_id:
            return jsonify({'message': 'clg_id is required'}), 400

        query_check_existence = "SELECT clg_id FROM college WHERE clg_id = %s"

        with psycopg2.connect(**db_params) as conn, conn.cursor() as cur:
            cur.execute(query_check_existence, (clg_id,))
            existing_college_id = cur.fetchone()

            if not existing_college_id:
                return jsonify({'message': 'College not found'}), 404

            query_delete_score = "DELETE FROM score WHERE stud_id IN (SELECT stud_id FROM student WHERE clg_id = %s)"
            cur.execute(query_delete_score, (clg_id,))

            query_delete_student = "DELETE FROM student WHERE clg_id = %s"
            query_delete_college_department = "DELETE FROM college_department WHERE college_clg_id = %s"
            query_delete_college = "DELETE FROM college WHERE clg_id = %s"

            cur.execute(query_delete_student, (clg_id,))
            cur.execute(query_delete_college_department, (clg_id,))
            cur.execute(query_delete_college, (clg_id,))
            conn.commit()

            deleted_rows = cur.rowcount

            if deleted_rows > 0:
                return jsonify({'message': f'College and associated data deleted successfully'})
            else:
                return jsonify({'message': 'No data deleted'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def add_student():
    if request.method == 'POST':
        try:
            if 'login_id' not in session or 'roll' not in session or session['roll'] != 'admin':
                return jsonify({'message': 'Unauthorized'}), 401

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

            with psycopg2.connect(**db_params) as conn, conn.cursor() as cursor:

                # Check if the email is unique
                if not is_email_unique(email, cursor):
                    return jsonify({'error': 'Email already exists!'})

                # Generate a simpler random password
                auto_generated_password = generate_password()

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
                conn.commit()

            # Send the email with student details
            send_mail(email, username, auto_generated_password,
                      data['stud_name'], '', '')  # Add middle and last name if available

            return jsonify({'message': 'Student added successfully!'})

        except psycopg2.IntegrityError as e:
            # Handle specific database integrity constraint violations
            return jsonify({'error': str(e)})

        except Exception as e:
            return jsonify({'error': str(e)})

def fetch_course():
    try:
        if 'login_id' not in session or 'roll' not in session or session['roll'] != 'admin':
            return jsonify({'message': 'Unauthorized'}), 401

        with psycopg2.connect(**db_params) as conn, conn.cursor() as cursor:
            # Fetch all courses
            cursor.execute('SELECT course_id, course_name FROM public.course;')

            # Fetch all the results
            result = cursor.fetchall()

            # Convert the result to a list of dictionaries for JSON response
            courses = [{'course_id': row[0], 'course_name': row[1]} for row in result]

            return jsonify({'courses': courses})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def addcourse():
    try:
        if 'login_id' not in session or 'roll' not in session or session['roll'] != 'admin':
            return jsonify({'message': 'Unauthorized'}), 401

        with psycopg2.connect(**db_params) as conn, conn.cursor() as cursor:
            # Extract data for the course table from JSON data
            data = request.get_json()
            sem_id = data.get('sem_id')
            course_name = data.get('course_name')

            # Check if sem_id is provided
            if not sem_id:
                return jsonify({'error': 'sem_id is required'}), 400

            # Check if the provided sem_id exists in the semester table
            cursor.execute("SELECT sem_id FROM public.semester WHERE sem_id = %s", (sem_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Invalid sem_id'}), 400

            # Check if the course with the same name already exists in the specified semester
            cursor.execute("SELECT course_id FROM public.course WHERE course_name = %s AND sem_id = %s", (course_name, sem_id))
            existing_course_id = cursor.fetchone()

            if existing_course_id:
                return jsonify({'error': 'Course with the same name already exists in the specified semester'}), 400

            # Insert data into the course table
            cursor.execute('''
                INSERT INTO public.course (course_name, sem_id)
                VALUES (%s, %s)
                RETURNING course_id;
            ''', (course_name, sem_id))

            # Fetch the generated course_id
            course_id = cursor.fetchone()[0]

            # Commit the transaction
            conn.commit()

            return jsonify({'message': 'Course added successfully', 'course_id': course_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    
def updatecourse():
    try:
        if 'login_id' not in session or 'roll' not in session or session['roll'] != 'admin':
            return jsonify({'message': 'Unauthorized'}), 401

        with psycopg2.connect(**db_params) as conn, conn.cursor() as cur:
            # Extract data from query parameters
            course_id = request.args.get('course_id')
            course_name = request.json.get('course_name')

            # Update data in the course table
            cur.execute('''
                UPDATE public.course
                SET course_name = %s
                WHERE course_id = %s;
            ''', (course_name, course_id))

            # Commit the transaction
            conn.commit()

        return jsonify({'message': 'Course updated successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    
def addscore():
    try:
        if 'login_id' not in session or 'roll' not in session or session['roll'] != 'admin':
            return jsonify({'message': 'Unauthorized'}), 401

        with psycopg2.connect(**db_params) as conn, conn.cursor() as cur:
            # Extract data for the score table from request parameters
            stud_id = request.args.get('stud_id')
            course_id = request.json.get('course_id')
            score = request.json.get('score')

            # Insert data into the score table
            cur.execute('''
                INSERT INTO public.score (stud_id, course_id, score)
                VALUES (%s, %s, %s);
            ''', (stud_id, course_id, score,))

            # Commit the transaction
            conn.commit()

        return jsonify({'message': 'Score added successfully'})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cur.close()
        conn.close()


def get_scores_by_stud_id_and_sem(stud_id, sem_no, cursor):
    # Get stud_name, course_id, course_name, and score associated with the stud_id and semester from the score table
    query = """
    SELECT student.stud_name, score.course_id, course.course_name, score.score
    FROM score
    JOIN course ON score.course_id = course.course_id
    JOIN semester ON course.sem_id = semester.sem_id
    JOIN student ON score.stud_id = student.stud_id
    WHERE score.stud_id = %s AND semester.sem_no = %s
    """
    cursor.execute(query, (stud_id, sem_no))
    results = cursor.fetchall()
    return results


def get_email_by_stud_id(stud_id, cursor):
    # Get the email associated with the stud_id from the student table
    query = "SELECT mail FROM student WHERE stud_id = %s"
    cursor.execute(query, (stud_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None


def send_email(recipient_email, subject, body):
    # SMTP server settings
    smtp_server = 'smtp-relay.brevo.com'  # Replace with your SMTP server
    smtp_port = 587  # Change to the appropriate port
    smtp_username = 'leadershipteam28@gmail.com'
    smtp_password = 'Ssvfa2nQdmPUDGZ0'
    smtp_sender_email = 'leadershipteam28@gmail.com'

    # Create a multipart message
    message = MIMEMultipart()
    message['From'] = smtp_sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Add message body
    message.attach(MIMEText(body, 'plain'))

    # Connect to SMTP server and send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)


def mailscore():
    if request.method == 'GET':
        try:
            # Get stud_id and sem_no from request parameters
            stud_id = request.args.get('stud_id')
            sem_no = request.args.get('sem_no')

            # Check if stud_id and sem_no are provided
            if not stud_id or not sem_no:
                return generate_response({'error': 'Missing parameters: stud_id or sem_no'},404)

            # Convert sem_no to integer
            sem_no = int(sem_no)

            # Database connection
            connection = db_conn()
            cursor = connection.cursor()

            # Get email by stud_id
            recipient_email = get_email_by_stud_id(stud_id, cursor)

            if recipient_email:
                # Get scores by stud_id and sem_no
                scores = get_scores_by_stud_id_and_sem(stud_id, sem_no, cursor)
                stud_name = scores[0][0] if scores else ''
                # Close connection
                cursor.close()
                connection.close()

                # Send email with score details
                email_body = generates_email_body(stud_id, sem_no, stud_name, scores)
                send_email(recipient_email, f'Semester {sem_no} Scores Added', email_body)

                return generate_response({'message': 'Email sent successfully!'})
            else:
                cursor.close()
                connection.close()
                return generate_response({'error': 'Email not found for the provided stud_id'},404)

        except Exception as e:
            return generate_response({'error': str(e)},500)
        
def generates_email_body(stud_id, sem_no, stud_name, scores):
    # Replace placeholders with actual values
    scores_table = ""
    for score in scores:
        scores_table += f"""
            <tr>
                <td>{score[1]}</td>
                <td>{score[2]}</td>
                <td>{score[3]}</td>
            </tr>
        """

    body = f"""
   <html>

<body style="font-family: 'Poppins', sans-serif; letter-spacing: -0.5px;">

    <div style="background-color: #9747FF; padding: 20px; text-align: center; color: #fff;">
         <img src="Logo.svg" alt="Stellar University Logo" width="100" height="100">
        <h1 style=>Stellar University</h1>
        <p>Inspiring Minds, Shaping Futures</p>
    </div>
    <div style="padding: 20px;">
        <h2 style="color: #9747FF;">Dear {stud_name},</h2>
        <p>We hope this email finds you well. Here are your scores for Semester {sem_no}:</p>
    </div>
    <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
        <thead>
            <tr style="background-color: #9747FF; color: #fff;">
                <th>Course ID</th>
                <th>Course Name</th>
                <th>Score</th>
            </tr>
        </thead>
        <tbody>
            {scores_table}
        </tbody>
    </table>
    <div style="padding: 20px;">
        <p>If you have any questions or concerns regarding your scores, feel free to contact us.</p>
        <p>Thank you for your dedication and hard work. We wish you continued success in your studies!</p>
    </div>

</body>

</html>

    """

    return body
