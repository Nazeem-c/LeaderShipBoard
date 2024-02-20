from flask import Flask, jsonify, request, redirect, url_for, session
from psycopg2.extras import RealDictCursor 
from datetime import timedelta
from config import db_params
import psycopg2
from utils.response import generate_response

app = Flask(__name__)
app.config['SECRET_KEY'] = 'leadershipboard'



# def login():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')

#     query = "SELECT login_id, username, roll FROM login WHERE username = %s AND password = %s"

#     try:
#         with psycopg2.connect(**db_params) as conn:
#             with conn.cursor() as cur:
#                 cur.execute(query, (username, password))
#                 user = cur.fetchone()

#         if user:
#             session['login_id'] = user[0]
#             session['username'] = user[1]
#             session['roll'] = user[2]

#             if user[2] == 'admin':
#                 return redirect(url_for('admin.adminpage'))
#             elif user[2] == 'student':
#                 return redirect(url_for('students.studentpage'))
#             else:
#                 return generate_response({'error': 'Invalid role'}, 401)
#         else:
#              generate_response({'error': 'Invalid credentials'}, 401)

#     except Exception as e:
#         return generate_response({'error': str(e)}, 500)


def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    query = "SELECT login_id, username, roll FROM login WHERE username = %s AND password = %s"

    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (username, password))
                user = cur.fetchone()

        if user:
            session['login_id'] = user[0]
            session['username'] = user[1]
            session['roll'] = user[2]

            if user[2] == 'admin':
                return jsonify({
                    'user_id': user[0],
                    'username': user[1],
                    'roll': user[2],
                    'redirect_url': url_for('admin.adminpage')
                })
            elif user[2] == 'student':
                return jsonify({
                    'user_id': user[0],
                    'username': user[1],
                    'roll': user[2],
                    'redirect_url': url_for('students.studentpage')
                })
            else:
                return generate_response({'error': 'Invalid role'}, 401)
        else:
            return generate_response({'error': 'Invalid credentials'}, 401)

    except Exception as e:
        return generate_response({'error': str(e)}, 500)

def logout():
    session.pop('login_id', None)
    session.pop('username', None)
    session.pop('roll', None)

    return generate_response({'message': 'Logout successful'})
#dfghjkl;'ghj
