from flask import Flask, render_template, request, url_for, session, redirect
from flask_pymongo import PyMongo
from models import DuckFeedingSession
import os

# Create Flask app
template_dir = os.path.abspath('templates')
app = Flask(__name__, template_folder=template_dir)

# Connect to Mongo and initialize database variables
app.config['MONGO_DBNAME'] = 'freshworks_duck_feeding_app'
app.config['MONGO_URI'] = 'mongodb://admin:Mlab1134206`@ds145359.mlab.com:45359/freshworks_duck_feeding_app'
mongo = PyMongo(app)

@app.route('/')
def render_form():
    # Render base template
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
    return 'SUBMITTED'

if __name__ == '__main__':
    app.run(debug=True)
