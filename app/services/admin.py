from flask import Flask, jsonify, request, redirect, url_for, session
from psycopg2.extras import RealDictCursor 
from datetime import timedelta
from config import db_params
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'leadershipboard'



def admin():
    if 'login_id' in session and 'roll' in session and session['roll'] == 'admin':
        # User is authenticated as admin
        return jsonify({'message': 'Welcome to the admin portal, ' + session['username']})
    else:
        return redirect(url_for('login'))
    