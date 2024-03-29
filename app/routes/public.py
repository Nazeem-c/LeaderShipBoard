
# from services.public import get_topper,get_topper_batch,get_topper_dept,get_topper_dept_batch,get_topper_college_dept,get_topper_college_dept_batch,get_all_students,get_students_details,get_leadership_board,get_topper_college_dept_batch_sem
from flask import Blueprint

from config import secret_key
from services.public import *
app.secret_key = secret_key

public_router=Blueprint("public",__name__,url_prefix="/api/v1")


#1 student
@public_router.route('/leaderboard', methods=['GET']) #full filter
def leaderboard_student():
    return leaderboard()

#2 college
@public_router.route('/collegeleaderboard', methods=['GET']) #full filter
def leaderboardcollege():
    return college_leaderboard()

#3 department
@public_router.route('/departmentleaderboard', methods=['GET']) #full filter
def leaderboard_dept():
    return department_leaderboard()

#4 for getting college list in select boxin froont end
@public_router.route('/collegelistselect', methods=['GET']) #full filter
def get_collegelist():
    return collegelistselect()

#% for getting department list in select boxin froont end
@public_router.route('/departmentslistselect', methods=['GET'])
def getdepartmentlists():
    return departmentlist()

#% for getting btaches list in select boxin froont end
@public_router.route('/btacheslistselect', methods=['GET'])
def getbtacheslists():
    return batcheslist()



@public_router.route('/leaderboardColleges', methods=['GET']) #common
def gettopper():
    return get_topper()

@public_router.route('/leaderboardCollege', methods=['GET']) #batch wise
def gettopperbatch():
    return get_topper_batch()

@public_router.route('/leaderboardCollegesdept', methods=['GET']) #dept wise
def gettopperdept():
    return get_topper_dept()


@public_router.route('/leaderboardCollegebatch', methods=['GET'])  #dept,batch wise
def gettopperdeptbatch():
    return get_topper_dept_batch()

@public_router.route('/leaderboardCollegedept', methods=['GET']) #college wise
def gettoppercollege():
    return get_topper_college_dept()

@public_router.route('/leaderboardCollegedeptbatch', methods=['GET']) #full filter
def gettopperfullfilter():
    return get_topper_college_dept_batch()

# @public_router.route('/leaderboard', methods=['GET']) #full filter
# def gettoppersemfilter():
#     return leaderboard()

@public_router.route('/students', methods=['GET'])
def studentscore():
    return get_all_students()

# Route to list students with details and scores for a specific batch
@public_router.route('/students', methods=['GET'])
def studentdetails():
    return get_students_details()

@public_router.route('/leadership-board', methods=['GET'])
def batchsem():
    return get_leadership_board()

#ranking college based on avg score and pass percentage
@public_router.route('/colleges', methods=['GET'])
def collegelist():
    return list_colleges()


#  based on the given college, it shows student rank in each batch in each department--IMP
@public_router.route('/college-info', methods=['GET'])
def collegeinfo():
    return get_college_info()


# Route to list students with details for a specific department name
@public_router.route('/studentses', methods=['GET'])
def studentdet():
    return get_students_details_dept()