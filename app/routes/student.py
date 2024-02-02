from flask import app
from config import db_params
from app import get_student_details


@app.route('/student/student-details', methods=['GET'])
def student_data():
    return get_student_details()