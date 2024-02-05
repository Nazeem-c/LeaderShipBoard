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

def get_topper_dept():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                dep_name = request.args.get('department')

        
                cur.execute('''
            SELECT s.stud_id, s.stud_name, a.score
            FROM student s
            JOIN score a ON s.stud_id = a.stud_id
            JOIN department d ON s.dep_id = d.dep_id
            WHERE d.dep_name = %s
            ORDER BY a.score DESC;
                ''', (dep_name,))

                dept_LeadershipBoard = cur.fetchall()
                return jsonify({'LeadershipBoard_department': dept_LeadershipBoard})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_topper_dept_batch():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                department = request.args.get('department')
                batch = request.args.get('batch')

                cur.execute('''
            SELECT s.stud_id, s.stud_name, d.dep_name, s.batch, SUM(sc.score) AS total_marks
            FROM student s
            JOIN score sc ON s.stud_id = sc.stud_id
            JOIN department d ON s.dep_id = d.dep_id
            WHERE d.dep_name = %s AND s.batch = %s
            GROUP BY s.stud_id, s.stud_name, d.dep_name, s.batch
            ORDER BY total_marks DESC;
            ''', (department, batch))

                dept_LeadershipBoard = cur.fetchall()
                return jsonify({'LeadershipBoard_dept_batch': dept_LeadershipBoard})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_topper_college_dept():
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                clg_name = request.args.get('clg_name')
                dep_name = request.args.get('dep_name')

                if not clg_name or not dep_name:
                    return jsonify({'error': 'Both clg_name and dep_name are required'}), 400

                cur.execute('''
            SELECT s.stud_id, s.stud_name, d.dep_name, SUM(sc.score) AS total_marks
            FROM student s
            JOIN score sc ON s.stud_id = sc.stud_id
            JOIN department d ON s.dep_id = d.dep_id
            JOIN college c ON s.clg_id = c.clg_id
            WHERE c.clg_name = %s AND d.dep_name = %s
            GROUP BY s.stud_id, s.stud_name, d.dep_name
            ORDER BY total_marks DESC;
                ''', (clg_name, dep_name))

                dept_LeadershipBoard = cur.fetchall()
                return jsonify({'LeadershipBoard_college_dept': dept_LeadershipBoard})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_topper_college_dept_batch():
    try:
        clg_name = request.args.get('clg_name')
        dep_name = request.args.get('dep_name')
        batch = request.args.get('batch')

        cur.execute('''
            SELECT s.stud_id, s.stud_name, d.dep_name, s.batch, SUM(sc.score) AS total_marks
            FROM student s
            JOIN score sc ON s.stud_id = sc.stud_id
            JOIN department d ON s.dep_id = d.dep_id
            JOIN college c ON s.clg_id = c.clg_id
            WHERE c.clg_name = %s AND d.dep_name = %s AND s.batch = %s
            GROUP BY s.stud_id, s.stud_name, d.dep_name, s.batch
            ORDER BY total_marks DESC;
        ''', (clg_name, dep_name, batch))

        dept_LeadershipBoard = cur.fetchall()
        return jsonify({'LeadershipBoard_college_dept_batch': dept_LeadershipBoard})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
