
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_session import Session
from datetime import timedelta
from config import secret_key


app = Flask(__name__)
CORS(app,supports_credentials= True) 
# app.config['SESSION_COOKIE_SAMESITE'] = 'None'
# app.config['SESSION_COOKIE_SECURE'] = True

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SAMESITE'] = 'none'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_COOKIE_SECURE'] = True
 


app.secret_key = secret_key
 # You can choose a different session type based on your needs
Session(app)

from routes.admin import admin_router
from routes.login import login_router
from routes.public import public_router
from routes.student import student_router


#blueprint registration
app.register_blueprint(admin_router)
app.register_blueprint(login_router)
app.register_blueprint(public_router)
app.register_blueprint(student_router)


if __name__ == '__main__':
    app.run(debug=True,port=5001)





















