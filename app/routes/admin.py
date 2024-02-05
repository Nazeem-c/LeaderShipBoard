from services.admin import admin,get_college,add_college,update_college,delete_college
from flask import Blueprint


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

