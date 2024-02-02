from flask import app
from config import db_params
from services.login import login


@app.route('/login', methods=['POST'])
def loginpage():
    return login()