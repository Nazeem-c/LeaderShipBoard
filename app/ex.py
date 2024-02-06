
 
app = Flask(__name__)
 
# Database configuration
db_params = {
    'dbname': 'LeaderShipBoard',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}
 
@app.route('/mail-score', methods=['POST'])

 
if __name__ == '__main__':
    app.run(debug=True)