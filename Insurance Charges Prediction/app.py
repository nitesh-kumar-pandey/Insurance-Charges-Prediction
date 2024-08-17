from flask import Flask, render_template, request
import sqlite3
import os
from sklearn.ensemble import RandomForestRegressor
import joblib
from datetime import datetime

app = Flask(__name__)

# Load the model once at the start
model = joblib.load('models\\randomforest_model.lb')

# Create a context manager for database connections
def get_db_connection():
    conn = None
    try:
        conn = sqlite3.connect('userdata.db')
        print(sqlite3.version)
        create_table_query = """
        CREATE TABLE IF NOT EXISTS userecord (
            age INTEGER,
            bmi REAL,
            child INTEGER,
            gender INTEGER,
            smoker INTEGER,
            northwest INTEGER,
            southeast INTEGER,
            southwest INTEGER,
            prediction INTEGER,
            date TEXT,
            time TEXT
        )
        """
        conn.execute(create_table_query)
    except sqlite3.Error as e:
        print(e)
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/project')
def project():
    return render_template('project.html')

@app.route('/records')
def records():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM userecord")
        records = cur.fetchall()
        cur.close()
        return render_template('records.html', records=records)

@app.route("/prediction", methods=['GET', 'POST'])
def prediction():
    if request.method == "POST":
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Input values
            age = int(request.form['age'])
            bmi = float(request.form['bmi'])  # BMI is usually a float
            child = int(request.form['child'])
            gender = int(request.form['gender'])
            smoker = int(request.form['smoker'])
            region = request.form['region']

            # region encoding
            northwest = 0
            southeast = 0
            southwest = 0

            if region == 'northwest':
                northwest = 1
            elif region == 'southeast':
                southeast = 1
            elif region == 'southwest':
                southwest = 1

            unseen_data = [[age, bmi, child, gender, smoker, northwest, southeast, southwest]]

            prediction = model.predict(unseen_data)[0]

            current_date = datetime.now()
            date = current_date.strftime('%d/%m/20%y')
            time = current_date.strftime("%H:%M")

            unseen_data_with_prediction = (age, bmi, child, gender, smoker, northwest, southeast, southwest, int(prediction), date, time)

            insert_data_query = """
            INSERT INTO userecord VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(insert_data_query, unseen_data_with_prediction)
            conn.commit()
            cur.close()

            return render_template('output.html', output=str(int(prediction)))

if __name__ == "__main__":
    app.run(debug=True)