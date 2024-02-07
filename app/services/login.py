from flask import Flask, jsonify, request, redirect, url_for, session
from psycopg2.extras import RealDictCursor 
from datetime import timedelta
from config import db_params
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'leadershipboard'



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
                return redirect(url_for('admin.adminpage'))
            elif user[2] == 'student':
                return redirect(url_for('students.studentpage'))
            else:
                return jsonify({'error': 'Invalid role'}), 401
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def logout():
    session.pop('login_id', None)
    session.pop('username', None)
    session.pop('roll', None)

    return jsonify({'message': 'Logout successful'})
#dfghjkl;'ghj
