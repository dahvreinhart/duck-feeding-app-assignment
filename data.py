from flask import Flask, render_template, request, url_for, session, redirect
from flask_pymongo import PyMongo
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
    return render_template('user_feeding_input_form.html')

@app.route('/submit_feeding_data', methods=['POST'])
def submit_feeding_data():
    return 'SUBMITTED'

if __name__ == '__main__':
    app.run(debug=True)
