from flask import Blueprint

from services.students import student,get_student_details,stud_average_score,get_current_semester
from flask import Blueprint
from services.login import *

from config import secret_key

from datetime import timedelta

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SAMESITE'] = 'none'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_COOKIE_SECURE'] = True
 


app.secret_key = secret_key


login_router= Blueprint('login', __name__,url_prefix='/api/v1')



@login_router.route('/login', methods=['POST'])  #login for entry
def loginpage():
    return login()



@login_router.route('/logout')  #logout for entry
def logoutpage():
    return logout()


