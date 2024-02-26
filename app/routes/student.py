
from services.students import *
from flask import Blueprint
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




app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SAMESITE'] = 'none'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_COOKIE_SECURE'] = True
 



app.secret_key = secret_key


student_router=Blueprint("students",__name__,url_prefix="/api/v1")


@student_router.route('/student')
def studentpage():
    return student()

@student_router.route('/student/student-details', methods=['GET'])
def student_data():
    print(session.get('username'))
    return get_student_details()

@student_router.route('/student/score', methods=['GET'])
def studentavg():
    return stud_semester_score()

@student_router.route('/student/current-semester', methods=['GET'])
def currentsemester():
    return get_current_semester()
