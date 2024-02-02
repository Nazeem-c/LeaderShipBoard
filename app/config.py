
# from flask import Flask, jsonify, request, redirect, url_for, session,Blueprint
# import psycopg2
# from psycopg2.extras import RealDictCursor 



# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'leadershipboard'  # Replace with a secure secret key

# def db_conn():
#     conn = psycopg2.connect(database="LeaderShipBoard", host="localhost", user="postgres", password="postgres", port="5432")
#     return conn


# conn = db_conn()
# cur = conn.cursor()


db_params = {'database': 'LeaderShipBoard', 'host': 'localhost', 'user': 'postgres', 'password':'postgres', 'port':'5432'}
