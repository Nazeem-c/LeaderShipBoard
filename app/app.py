# from flask import app
# from config import db_params
# from services.public import get_topper,get_topper_batch,get_topper_dept,get_topper_dept_batch,get_topper_college_dept,get_topper_college_dept_batch,get_all_students,get_students_details,get_leadership_board
# from services.admin import admin,get_college,add_college,update_college,delete_college
# from services.login import login,logout
# from services.students import student,get_student_details,stud_average_score,get_current_semester
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'leadershipboard'


from routes.admin import admin_router
from routes.login import login_router
from routes.public import public_router
from routes.student import student_router


#blueprint registration
app.register_blueprint(admin_router)
app.register_blueprint(login_router)
app.register_blueprint(public_router)
app.register_blueprint(student_router)



#Error Handler
# @app.errorhandler(Exception)
# def handle_error(error):
#     # You can customize this function based on your error-handling needs
#     response = {
#         'error': 'An unexpected error occurred',
#         'message': str(error)
#     }
#     return jsonify(response), 500

# #----------------------------------------------------commoc entry--------------------------------------------------
# @app.route('/leaderboardColleges', methods=['GET']) #common
# def gettopper():
#     return get_topper()

# @app.route('/leaderboardCollege', methods=['GET']) #batch wise
# def gettopperbatch():
#     return get_topper_batch()

# @app.route('/leaderboardCollegesdept', methods=['GET']) #dept wise
# def gettopperdept():
#     return get_topper_dept()


# @app.route('/leaderboardCollegebatch', methods=['GET'])  #dept,batch wise
# def gettopperdeptbatch():
#     return get_topper_dept_batch()

# @app.route('/leaderboardCollegedept', methods=['GET']) #college wise
# def gettoppercollege():
#     return get_topper_college_dept()

# @app.route('/leaderboardCollegedeptbatch', methods=['GET']) #full filter
# def gettopperfullfilter():
#     return get_topper_college_dept_batch()

# #-----------------------------shez----------------

# # Route to get all students with scores for each course
# @app.route('/students', methods=['GET'])
# def studentscore():
#     return get_all_students()

# # Route to list students with details and scores for a specific batch
# @app.route('/students', methods=['GET'])
# def studentdetails():
#     return get_students_details()


# #--------------------------------vadhi-------------------


# @app.route('/leadership-board', methods=['GET'])
# def batchsem():
#     return get_leadership_board()






#--------------------------------------------
# --------login entry---------------------------------------------------
# @app.route('/login', methods=['POST'])  #login for entry
# def loginpage():
#     return login()



# @app.route('/logout')  #logout for entry
# def logoutpage():
#     return logout()
#----------------------------------------------STUDENT---------------------------------------------------

# @app.route('/student')
# def studentpage():
#     return student()

# @app.route('/student/student-details', methods=['GET'])
# def student_data():
#     return get_student_details()

# @app.route('/student/averagescore', methods=['GET'])
# def studentavg():
#     return stud_average_score()

# @app.route('/student/current-semester', methods=['GET'])
# def currentsemester():
#     return get_current_semester()


# #-------------------------------------------------------admin operations---------------------------------------------

# @app.route('/admin') 
# def adminpage():
#     return admin()

# #-------------------------------------- college operation--------------------------------------

# @app.route('/college', methods=['GET'])
# def college():
#     return get_college()

# @app.route('/college', methods=['POST'])
# def addcollege():
#     return add_college()

# @app.route('/college', methods=['PUT'])
# def updatecollege():
#     return update_college()

# @app.route('/college', methods=['DELETE'])
# def deletecollege():
#     return delete_college()





if __name__ == '__main__':
    app.run(debug=True,port=5001)























if __name__ == '__main__':
    app.run(debug=True,port=5001)    
