from flask import Flask, jsonify, request, redirect, url_for, session
from psycopg2.extras import RealDictCursor 
from datetime import timedelta
from config import db_params
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'leadershipboard'


def get_topper():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT s.stud_id, s.stud_name, SUM(sc.score) AS total_marks
                    FROM student s
                    JOIN score sc ON s.stud_id = sc.stud_id
                    GROUP BY s.stud_id, s.stud_name
                    ORDER BY total_marks DESC;
                ''')

                College_LeadershipBoard = cur.fetchall()
                return jsonify({'LeadershipBoard': College_LeadershipBoard})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_topper_batch():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                # Retrieve batch from query parameter
                batch = request.args.get('batch')

                # Check if batch is provided
                if not batch:
                    return jsonify({'error': 'Batch parameter is required'}), 400

                cur.execute('''
                    SELECT s.stud_id, s.stud_name, s.batch, SUM(sc.score) AS total_marks
                    FROM student s
                    JOIN score sc ON s.stud_id = sc.stud_id
                    WHERE s.batch = %s
                    GROUP BY s.stud_id, s.stud_name, s.batch
                    ORDER BY total_marks DESC;
                ''', (batch,))

                batch_LeadershipBoard = cur.fetchall()
                return jsonify({'LeadershipBoard_batch': batch_LeadershipBoard})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
