from datetime import datetime

class DuckFeedingSession():
    collection_name = 'duck_feeding_sessions'

    def __init__(self, feeding_form_data):
        self.created_date = datetime.now()

        # Parse any passed in values from a feeding habits submission form
        self.location = feeding_form_data.get('location', '')
        self.feeding_time = feeding_form_data.get('feeding_time', '')
        self.number_of_ducks = feeding_form_data.get('number_of_ducks', '')
        self.food_type = feeding_form_data.get('food_type', '')
        self.specific_food = feeding_form_data.get('specific_food', '')
        self.food_quantity_grams = feeding_form_data.get('food_quantity_grams', '')

    def storable(self):
        return self.__dict__

    def __repr__(self):
        print self.storable()
