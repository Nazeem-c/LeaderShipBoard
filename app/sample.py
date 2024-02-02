from flask import Flask, jsonify, request
import psycopg2
# from init_db import db_conn

app = Flask(__name__)
def db_conn():
    conn = psycopg2.connect(database = "LeaderShipBoard",host="localhost",user="postgres",password="postgres",port="5432");
    return conn

conn = db_conn()
cur = conn.cursor()




#batcwise only


@app.route('/leaderboardCollege', methods=['GET'])
def get_topper_batch():
    try:
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

# for finding department topper using dept_id

@app.route('/leaderboardColleges', methods=['GET'])
def get_topper_dept():
    try:
        
        dep_id = request.args.get('department')

        
        cur.execute('''
            SELECT s.stud_id, s.stud_name, SUM(a.score) AS total_marks
            FROM student s
            JOIN score a ON s.stud_id = a.stud_id
            JOIN department d ON s.dep_id = d.dep_id
            WHERE d.dep_id = %s
            GROUP BY s.stud_id, s.stud_name
            ORDER BY total_marks DESC;
        ''', (dep_id,))

        dept_LeadershipBoard = cur.fetchall()
        return jsonify({'LeadershipBoard_department': dept_LeadershipBoard})

    except Exception as e:
        return jsonify({'error': str(e)}), 500



# for finding department topper usind dept_name
@app.route('/leaderboardCollegesdept', methods=['GET'])
def get_topper_dept_name():
    try:
        # Get the department name from the query parameters
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




#batch wise
 

@app.route('/leaderboardCollege', methods=['GET'])
def get_topper_dept_batch():
    try:
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




# for finding department topper, college wise
    
@app.route('/leaderboardCollege', methods=['GET'])
def get_topper_college_dept():
    try:
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

#for getting batchwise filter

@app.route('/leaderboardCollege', methods=['GET'])
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


if __name__ == '__main__':
    app.run(debug=True,port=5000)