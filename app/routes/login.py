from flask import Blueprint
from services.login import login,logout


login_router= Blueprint('login', __name__,url_prefix='/api/v1')



@login_router.route('/login', methods=['POST'])  #login for entry
def loginpage():
    return login()



@login_router.route('/logout')  #logout for entry
def logoutpage():
    return logout()


