# from flask import app
from config import db_params
from services.public import get_topper,get_topper_batch,get_topper_dept,get_topper_dept_batch,get_topper_college_dept,get_topper_college_dept_batch
from services.admin import admin,get_college
from services.login import login,logout
from services.students import student,get_student_details,stud_average_score,get_current_semester
from flask import Flask, jsonify, request


app = Flask(__name__)
app.config['SECRET_KEY'] = 'leadershipboard'


#----------------------------------------------------commoc entry--------------------------------------------------
@app.route('/leaderboardColleges', methods=['GET']) #common
def gettopper():
    return get_topper()

@app.route('/leaderboardCollege', methods=['GET']) #batch wise
def gettopperbatch():
    return get_topper_batch()

@app.route('/leaderboardCollegesdept', methods=['GET']) #dept wise
def gettopperdept():
    return get_topper_dept()


@app.route('/leaderboardCollegebatch', methods=['GET'])  #dept,batch wise
def gettopperdeptbatch():
    return get_topper_dept_batch()

@app.route('/leaderboardCollegedept', methods=['GET']) #college wise
def gettoppercollege():
    return get_topper_college_dept()

@app.route('/leaderboardCollegedeptbatch', methods=['GET']) #full filter
def gettopperfullfilter():
    return get_topper_college_dept_batch()

#----------------------------------------------------login entry---------------------------------------------------
@app.route('/login', methods=['POST'])  #login for entry
def loginpage():
    return login()



@app.route('/logout')  #logout for entry
def logoutpage():
    return logout()
#----------------------------------------------STUDENT---------------------------------------------------

@app.route('/student')
def studentpage():
    return student()

@app.route('/student/student-details', methods=['GET'])
def student_data():
    return get_student_details()

@app.route('/student/averagescore', methods=['GET'])
def studentavg():
    return stud_average_score()

@app.route('/student/current-semester', methods=['GET'])
def currentsemester():
    return get_current_semester()


#-------------------------------------------------------admin operations---------------------------------------------

@app.route('/admin') 
def adminpage():
    return admin()

@app.route('/college', methods=['GET'])
def college():
    return get_college()





if __name__ == '__main__':
    app.run(debug=True,port=5001)























if __name__ == '__main__':
    app.run(debug=True,port=5001)    
