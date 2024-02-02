# from flask import app
from config import db_params
from services.admin import admin
from services.login import login,logout
from services.students import student,get_student_details
from flask import Flask, jsonify, request


app = Flask(__name__)
app.config['SECRET_KEY'] = 'leadershipboard'


@app.route('/login', methods=['POST'])  #login for entry
def loginpage():
    return login()

@app.route('/admin') 
def adminpage():
    return admin()

@app.route('/student')
def studentpage():
    return student()

@app.route('/student/student-details', methods=['GET'])
def student_data():
    return get_student_details()





@app.route('/logout')  #logout for entry
def logoutpage():
    return logout()

if __name__ == '__main__':
    app.run(debug=True,port=5001)























if __name__ == '__main__':
    app.run(debug=True,port=5001)    
