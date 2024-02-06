from flask import Flask, request, jsonify
import psycopg2
import re
import uuid
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import db_params  # Assuming you have a config file named 'config.py'

app = Flask(__name__)

# Database configuration
db_params = {
    'dbname': 'LeaderShipBoardV1',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

def db_conn():
    conn = psycopg2.connect(**db_params)
    return conn

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

def send_mail(email, subject, body):
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
    message['Subject'] = subject

    # Add message body
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

@app.route('/student', methods=['GET'])
def add_student():
    if request.method == 'POST':
        try:
            stud_id = request.json.get('stud_id')

            # Check if stud_id is provided
            if not stud_id:
                return jsonify({'error': 'stud_id is required'}), 400

            # Database connection
            with psycopg2.connect(**db_params) as conn, conn.cursor() as cursor:

                # Check if stud_id already exists
                cursor.execute("SELECT stud_id FROM student WHERE stud_id = %s", (stud_id,))
                existing_stud_id = cursor.fetchone()

                if existing_stud_id:
                    return jsonify({'error': 'Student with the same stud_id already exists'}), 400

                # Insert into student table
                cursor.execute('''
                    INSERT INTO student (stud_id)
                    VALUES (%s)
                ''', (stud_id,))

                # Commit changes and close connection
                conn.commit()

            # Fetch the student's scores
            connection = db_conn()
            cursor = connection.cursor()
            cursor.execute('''
                SELECT course.course_name, score.score
                FROM public.course
                JOIN public.score ON course.course_id = score.course_id
                WHERE score.stud_id = %s;
            ''', (stud_id,))
            scores = cursor.fetchall()

            # Construct the email body with score details
            email_body = f"Dear Student with stud_id {stud_id},\n\nHere are your score details:\n\n"
            for course_name, score in scores:
                email_body += f"{course_name}: {score}\n"

            # Close connection
            cursor.close()
            connection.close()

            # Send the email with student details
            send_mail('student@example.com', 'Score Details - University Portal', email_body)

            return jsonify({'message': 'Student added successfully!'})

        except psycopg2.IntegrityError as e:
            # Handle specific database integrity constraint violations
            return jsonify({'error': str(e)}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
