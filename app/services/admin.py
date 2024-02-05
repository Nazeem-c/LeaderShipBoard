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


def get_college():
    query = """
        SELECT c.clg_id, c.clg_name, c.contact, c.established_year, a.place, a.state, a.pin
        FROM college c
        JOIN address a ON c.addr_id = a.addr_id
    """

    with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                results = cur.fetchall()

                colleges = []

                for result in results:
                    clg_id, clg_name, contact, established_year, place, state, pin = result

                    college_info = {
            'clg_id': clg_id,
            'clg_name': clg_name,
            'contact': contact,
            'established_year': established_year,
            'place': place,
            'state': state,
            'pin': pin
        }

                    colleges.append(college_info)

    return jsonify({'colleges': colleges})
