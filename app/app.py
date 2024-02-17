
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

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


if __name__ == '__main__':
    app.run(debug=True,port=5001)























if __name__ == '__main__':
    app.run(debug=True,port=5001)    
