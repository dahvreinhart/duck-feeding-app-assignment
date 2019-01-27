from datetime import datetime

class DuckFeedingSession():
    collection_name = 'duck_feeding_sessions'

    def __init__(self, initialization_data):
        self.created_date = datetime.now()

        # Parse any passed in values from a feeding habits submission form
        self.location = initialization_data.get('location', '')
        self.feeding_time = initialization_data.get('feeding_time', '')
        self.number_of_ducks = initialization_data.get('number_of_ducks', '')
        self.food_type = initialization_data.get('food_type', '')
        self.specific_food = initialization_data.get('specific_food', '')
        self.food_quantity_grams = initialization_data.get('food_quantity_grams', '')
        self.is_recurring = initialization_data.get('make_recurring', False)

    def storable(self):
        return self.__dict__

    def __repr__(self):
        print self.storable()
