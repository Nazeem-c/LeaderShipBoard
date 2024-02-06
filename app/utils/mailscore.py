from flask import Flask, jsonify, request, redirect, url_for, session
from config import db_params
import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def add_score():
    if request.method == 'POST':
        try:
            data = request.get_json()
 
            # Check if required field is present
            if 'stud_id' not in data:
                return jsonify({'error': 'Missing required field: stud_id'})
 
            # Database connection
            connection = db_conn()
            cursor = connection.cursor()
 
            # Get email by stud_id
            recipient_email = get_email_by_stud_id(data['stud_id'], cursor)
 
            if recipient_email:
                # Get scores by stud_id
                scores = get_scores_by_stud_id(data['stud_id'], cursor)
 
                # Close connection
                cursor.close()
                connection.close()
 
                # Send email with score details
                email_body = generate_email_body(data['stud_id'], scores)
                send_email(recipient_email, 'Scores Added', email_body)
                return jsonify({'message': 'Email sent successfully!'})
            else:
                cursor.close()
                connection.close()
                return jsonify({'error': 'Email not found for the provided stud_id'})
 
        except Exception as e:
            return jsonify({'error': str(e)})
 
def generate_email_body(stud_id, scores):
    body = f"Scores for Student ID {stud_id}:\n"
    for course_id, score in scores:
        body += f"Course ID: {course_id}, Score: {score}\n"
    return body


def db_conn():
    return psycopg2.connect(**db_params)
 
def get_scores_by_stud_id(stud_id, cursor):
    # Get all scores associated with the stud_id from the score table
    query = "SELECT course_id, score FROM score WHERE stud_id = %s"
    cursor.execute(query, (stud_id,))
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
 
    # Connect to SMTP server and send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)
 



