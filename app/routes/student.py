
from services.students import student,get_student_details,stud_average_score,get_current_semester
from flask import Blueprint


student_router=Blueprint("students",__name__,url_prefix="/api/v1")


@student_router.route('/student')
def studentpage():
    return student()

@student_router.route('/student/student-details', methods=['GET'])
def student_data():
    return get_student_details()

@student_router.route('/student/averagescore', methods=['GET'])
def studentavg():
    return stud_average_score()

@student_router.route('/student/current-semester', methods=['GET'])
def currentsemester():
    return get_current_semester()
