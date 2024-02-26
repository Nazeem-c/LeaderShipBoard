from services.admin import *
from flask import Blueprint

from config import secret_key

app.secret_key = secret_key

admin_router= Blueprint('admin', __name__,url_prefix='/api/v1')



@admin_router.route('/admin') 
def adminpage():
    return admin()

#-------------------------------------- college operation--------------------------------------

@admin_router.route('/college', methods=['GET'])
def college():
    return get_college()

@admin_router.route('/college', methods=['POST'])
def addcollege():
    return add_college()

@admin_router.route('/college', methods=['PUT'])
def updatecollege():
    return update_college()

@admin_router.route('/college', methods=['DELETE'])
def deletecollege():
    return delete_college()

@admin_router.route('/student', methods=['POST'])
def addstudent():
    return add_student()


#----------------------------------course---------------------------------------------

@admin_router.route('/course', methods=['GET'])
def get_course():
    return fetch_course()

#addcourse 
@admin_router.route('/course', methods=['POST'])   
def add_course():
    return addcourse()

#updateCourse
@admin_router.route('/course', methods=['PUT'])
def update_course():
    return updatecourse()


#------------------------------------score---------------------------------------


@admin_router.route('/score', methods=['POST'])
def add_score():
    return addscore()



@admin_router.route('/mail-score', methods=['POST'])
def mail_score():
    return mailscore()