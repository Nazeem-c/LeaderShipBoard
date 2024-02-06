
import re
import uuid
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
 
 
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
 