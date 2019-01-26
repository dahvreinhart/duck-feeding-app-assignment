from flask import Flask, render_template, request, url_for, session, redirect, send_file, Response
from flask_pymongo import PyMongo
from models import DuckFeedingSession
from datetime import datetime
import os
import csv

# Create Flask app
template_dir = os.path.abspath('templates')
downloads_dir = os.path.abspath('temp_data_files')
app = Flask(__name__, template_folder=template_dir)

# Connect to Mongo and initialize database variables
app.config['MONGO_DBNAME'] = 'freshworks_duck_feeding_app'
app.config['MONGO_URI'] = 'mongodb://admin:Mlab1134206`@ds145359.mlab.com:45359/freshworks_duck_feeding_app'
app.config['TEMP_DATA_FILES_FOLDER'] = downloads_dir
mongo = PyMongo(app)

@app.route('/')
def render_form():
    # Render base template with input form
    return render_template('user_feeding_input_form.html')

@app.route('/submit_feeding_data', methods=['POST'])
def submit_feeding_data():
    # Parse feeding habits submittion form data from template
    form_data = {
        'location': request.form['location'],
        'feeding_time': request.form['feeding_time'],
        'number_of_ducks': request.form['number_of_ducks'],
        'food_type': request.form['food_type'],
        'specific_food': request.form['specific_food'],
        'food_quantity': request.form['food_quantity']
    }

    # Create a new feeding session object and write it to the database
    new_feeding_session = DuckFeedingSession(form_data)
    feedback_data = mongo.db.duck_feeding_sessions
    feedback_data.insert(new_feeding_session.storable())
    return render_template('after_successful_submission.html')

@app.route('/get_feeding_data_csv_download', methods=['GET'])
def get_feeding_data_csv_download():
    filename = "temp_data_file_{}.csv".format(datetime.now().strftime('%Y%m%d%H%M%S%f'))
    with open("{}/{}".format(app.config['TEMP_DATA_FILES_FOLDER'], filename), 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')

        # Write the column headers
        csv_writer.writerow([
            'DATE OF SUBMISSION',
            'FEEDING TIME (24h)',
            'LOCATION',
            'NUMBER OF DUCKS FED',
            'FOOD TYPE',
            'SPECIFIC FOOD',
            'FOOD QUANTITY (g)'
        ])

        feedback_data = mongo.db.duck_feeding_sessions.find()
        for item in feedback_data:
            created_date = item.get('created_date', '')
            if created_date:
                formatted_created_date = created_date.strftime('%Y/%m/%d')

            csv_writer.writerow([
                formatted_created_date,
                item.get('feeding_time', ''),
                item.get('location', ''),
                item.get('number_of_ducks', ''),
                item.get('food_type', ''),
                item.get('specific_food', ''),
                item.get('food_quantity', ''),
            ])


    csv_data = ''
    with open("{}/{}".format(app.config['TEMP_DATA_FILES_FOLDER'], filename)) as data:
        csv_data = data.read()

    os.remove("{}/{}".format(app.config['TEMP_DATA_FILES_FOLDER'], filename))

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename={}".format(filename)}
     )

if __name__ == '__main__':
    app.run(debug=True)
