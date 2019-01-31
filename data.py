from flask import Flask, render_template, request, url_for, session, redirect, send_file, Response
from flask_pymongo import PyMongo
from models import DuckFeedingSession
from datetime import datetime, timedelta
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
import os
import csv
import random

# Create Flask app
template_dir = os.path.abspath('templates')
app = Flask(__name__, template_folder=template_dir)

# Connect to Mongo and initialize database variables
app.config['MONGO_DBNAME'] = 'freshworks_duck_feeding_app'
app.config['MONGO_URI'] = 'mongodb://admin:Mlab1134206`@ds145359.mlab.com:45359/freshworks_duck_feeding_app'
mongo = PyMongo(app)

# initialize scheduler for recurring submissions
scheduler = BackgroundScheduler(timezone=utc)
scheduler.start()


@app.route('/')
def render_form():
    """ Base route - home page. """
    # Render base template with input form
    return render_template('user_feeding_input_form.html')

@app.route('/after_successful_submission')
def render_after_successful_submission():
    random_photo_filename = "images/after_submission_photo_{}.jpeg".format(random.randint(1, 6))
    return render_template('after_successful_submission.html', photo_filename=random_photo_filename)

@app.route('/submit_feeding_data', methods=['POST', 'GET'])
def submit_feeding_data():
    """ Handles the submission of user data from the front end form into the database. """
    # If someone is trying to route directly to this endpoint, bump them back to the home page for better UX
    if request.method == 'GET':
        return redirect("/", code=302)

    # Parse feeding habits submittion form data from template
    form_data = {
        'location': request.form.get('location', ''),
        'feeding_time': request.form.get('feeding_time', ''),
        'number_of_ducks': request.form.get('number_of_ducks', ''),
        'food_type': request.form.get('food_type', ''),
        'specific_food': request.form.get('specific_food', ''),
        'food_quantity_grams': request.form.get('food_quantity_grams', ''),
        'make_recurring': bool(request.form.get('make_recurring', False))
    }

    # Grab the database collection we will be writing to
    feedback_data = mongo.db.duck_feeding_sessions

    # Create a new feeding session object
    new_feeding_session = DuckFeedingSession(form_data)

    # Write the new feeding seeion object to the databse
    feedback_data.insert(new_feeding_session.storable())

    # Redirect the user to rendering function to protect against erroneous resubmissions via page reloads
    return redirect("/after_successful_submission")


@app.route('/get_feeding_data_csv_download', methods=['GET'])
def get_feeding_data_csv_download():
    """ Handles the making of a csv file and the handoff of that file to the user. """
    # Create a unique filename from the current date
    filename = "temp_data_file_{}.csv".format(datetime.now().strftime('%Y%m%d%H%M%S%f'))

    # Generate a temporary csv file of feeding session data
    generate_temp_csv(filename)

    # Read the csv data back into memory so that we can delete our temp file and save disk space
    csv_data = ''
    with open(filename) as data:
        csv_data = data.read()

    # Delete the temp file once we have the csv data to free disk space
    os.remove(filename)

    # Return the file to the user without redirecting them
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename={}".format(filename)}
     )


def generate_temp_csv(filename):
    """ Generate a temp csv file and save it so that it can later be downloaded by the user. """
    with open(filename, 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')

        # Write the column headers
        csv_writer.writerow([
            'DATE OF SUBMISSION',
            'FEEDING TIME (24h)',
            'LOCATION',
            'NUMBER OF DUCKS FED',
            'FOOD TYPE',
            'SPECIFIC FOOD',
            'FOOD QUANTITY (g)',
            'CREATED FROM RECURRING SUBMISSION'
        ])

        # Fetch the submission objects from the database
        feedback_data = mongo.db.duck_feeding_sessions.find()

        for item in feedback_data:
            # Format the created_date datetime object to something more readable
            created_date = item.get('created_date', '')
            if created_date:
                created_date = created_date.strftime('%Y/%m/%d')

            # Write the data for one feeding session to a row in the csv file
            csv_writer.writerow([
                created_date,
                item.get('feeding_time', ''),
                item.get('location', ''),
                item.get('number_of_ducks', ''),
                item.get('food_type', ''),
                item.get('specific_food', ''),
                item.get('food_quantity_grams', ''),
                item.get('is_recurring', ''),
            ])

@scheduler.scheduled_job(trigger='cron', hour=11, minute=30) # The scheduled job will run at 3:30am PST
def process_recurring_submissions():
    """ Automatically submits duplicates of past submissions that are maked as recurring. """
    duck_feeding_sessions = mongo.db.duck_feeding_sessions

    # Get all recurring submissions thatwere created less than a week ago
    initial_submission_cutoff = datetime.now() - timedelta(days=6)
    recurring_submissions = duck_feeding_sessions.find({
        'is_recurring': True,
        'created_date': {'$gte': initial_submission_cutoff}
    })

    # Go through each recurring subscription and clone it
    for submission in recurring_submissions:
        # First we make the clone from the full value of the initial submission
        new_automated_submission = DuckFeedingSession(submission)

        # Now we must correct the created date for data integrity and the is_recurring property
        # since we don't want the automated submissions to be recurring themselves
        new_automated_submission.created_date = datetime.now()
        new_automated_submission.is_recurring = False

        # Lastly, store the cloned submission in the Database
        duck_feeding_sessions.insert(new_automated_submission.storable())

    return True

#if __name__ == '__main__':
    # app.run(debug=True)
