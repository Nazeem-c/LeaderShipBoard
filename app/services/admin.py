from flask import Flask, jsonify, request, redirect, url_for, session
from psycopg2.extras import RealDictCursor 
from datetime import timedelta
from config import db_params
import psycopg2

import psycopg2
import re
import uuid
import random
import string
import smtplib
from email.mime.text import MIMEText





app = Flask(__name__)
app.config['SECRET_KEY'] = 'leadershipboard'



def admin():
    if 'login_id' in session and 'roll' in session and session['roll'] == 'admin':
        # User is authenticated as admin
        return jsonify({'message': 'Welcome to the admin portal, ' + session['username']})
    else:
        return redirect(url_for('login'))

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
 
def is_email_unique(email, cursor):
    # Check if the email is unique in the database
    query = "SELECT COUNT(*) FROM student WHERE mail = %s"
    cursor.execute(query, (email,))
    count = cursor.fetchone()[0]
    return count == 0
 
def send_mail(email, username, password, fname, mname, lname):
    recipient_email = email
    
    # SMTP server settings
    smtp_server = 'smtp-relay.brevo.com'
    port = 587  # Change to 465 if using SSL
    smtp_username = 'teamsmv02@gmail.com'
    smtp_password = 'bTOSmPMkJEdpsFL1'
    smtp_sender_email = 'teamsmv02@gmail.com'
 
    # Create a multipart message
    message = MIMEMultipart()
    message['From'] = smtp_sender_email
    message['To'] = recipient_email
    message['Subject'] = 'Login Credentials - University Portal'
 
    # Add message body
    body = f"""
Dear {fname} {mname} {lname},
 
Welcome to the University Portal! Below are your login credentials:
 
Username: {username}
Temporary Password: {password}
 
"""
    message.attach(MIMEText(body, 'plain'))
 
    server = None  # Initialize the variable
 
    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(smtp_username, smtp_password)
 
        # Send the email
        server.send_message(message)
        print(f'Email sent to {recipient_email}!')
    except smtplib.SMTPAuthenticationError as e:
        print(f'Authentication failed. Check your credentials. {e}')
    except smtplib.SMTPException as e:
        print(f'Error while sending email. {e}')
    finally:
        if server:
            # Disconnect from the server
            server.quit()
 

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

            # Database connection
            with psycopg2.connect(**db_params) as conn:
                with conn.cursor() as cursor:

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
