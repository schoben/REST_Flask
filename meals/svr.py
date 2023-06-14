"""
Exercise 1# for Cloud Computing course
Creating a server docker image implementing a REST API
"""

# Built-in imports
import os
from collections import namedtuple

# pip imports
from flask import Flask  # , jsonify
from flask_restful import Resource, Api, reqparse
import requests
import pymongo
import traceback


# Setting up global variables
# TODO: extract to a function
app = Flask(__name__)  # initialize Flask
api = Api(app)  # create API
ninja_api_key = 'GZhBLJkOriPZwhCOJlOdHg==UEeUzdzoKypBxfto'
    #os.environ['NINJA_API_KEY']
client = pymongo.MongoClient("mongodb://mongo:27017/")

# initializing the database
db = client["food"]
dishes_col = db["dishes"]  # TODO: dish the dish
meals_col = db["meals"]
# diets_col = db["diets"]
counters_col = db["counter"]

# TODO export to a function
# Initializing counters
counters = counters_col.find_one({'_id': 0})
if counters is None:
    print("Couldn't find any counters! Initializing counters to 0")
    counters_col.insert_one({'_id': 0, 'dishes': 0, 'meals': 0})
else:
    print(f"Found counters: {counters}")

'''
dishes_idx = counters.get('dishes', 0)
meals_idx = counters.get('meals', 0)
diets_idx = counters.get('diets', 0)
mydict = {'_id': 0, 'dish_idx': dishes_idx, 'meals_idx': meals_idx, 'diets_idx': diets_idx}
counter_col.insert_one(mydict)  # TODO: use update instead of insert
'''


# Creating a namedtuple for storing dish values
DishValues = namedtuple('DishValues', ['size', 'cal', 'sugar', 'sodium'])


# TODO: move following two function to a different module. Consider encapsulating in a class
def query_ninja(query):  # TODO: Deal with failures (no connection, unrecognized) 
    api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(query)
    response = requests.get(api_url, headers={'X-Api-Key': ninja_api_key}) 
    print(f"Got the following response from Ninja: {response} {response.json()}")
    if response.json() == []:
        raise ValueError("API-Ninja couldn't parse dish named {query}")
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        raise Exception("Error:", response.status_code, response.text)


def parse_ninja(res):
    size = 0
    cal = 0
    sugar = 0
    sodium = 0
    for dish_dict in res:
        size += dish_dict['serving_size_g']
        cal += dish_dict['calories']
        sugar += dish_dict['sugar_g']
        sodium += dish_dict['sodium_mg']
    return DishValues(size=size, cal=cal, sugar=sugar, sodium=sodium)


def parse_cursor(cursor):
    parsed_dict = list(cursor)
    for d in parsed_dict:
        del d['_id']
    return {d['ID']: d for d in parsed_dict}


# TODO: Move these two classes to a separate module (decouple), together with Meal and MealsCollection
class Dish:
    """Class representing a single dish"""

    def __init__(self, name, idx):
        self.idx = idx
        self.name = name
        ninja_response = query_ninja(self.name)
        dish_vals = parse_ninja(ninja_response)
        self.size = dish_vals.size
        self.cal = dish_vals.cal
        self.sugar = dish_vals.sugar
        self.sodium = dish_vals.sodium

    def _get_idx(self):
        return self.idx

    def _get_name(self):  # TODO: Use property instead of getter
        return self.name

    def get_cal(self):
        return self.cal

    def get_sugar(self):
        return self.sugar

    def get_sodium(self):
        return self.sodium

    def get_as_dict(self):
        return {'name': self.name, 'ID': self.idx, 'cal': self.cal, 'size': self.size, 'sodium': self.sodium, 'sugar': self.sugar}


class DishesCollection:
    """Collection class of all the dishes"""

    def __init__(self):
        self.dishes = dict()
        self.num_of_dishes = 0

    def _get_all_dishes(self):
        return {idx: dish.get_as_dict() for idx, dish in self.dishes.items()}

    def get_dish_by_idx(self, idx):
        return self.dishes[idx]

    def get_dish_by_name(self, name):
        for _, dish in self.dishes.items():  # Use .values() instead
            if dish._get_name() == name:
                return dish
        raise ValueError(f"Couldn't find a dish that goes by the name {name}")

    def dish_exists(self, name):
        '''func that checks if the dish exists in the db'''
        try:
            self.get_dish_by_name(name)
            return True
        except ValueError:
            return False

    def add_dish(self, name):
        print(f"Adding to Dishes: name {name}, idx: {self.num_of_dishes}")
        dish = Dish(name, self.num_of_dishes + 1)
        self.num_of_dishes += 1  # No support for concurrency
        self.dishes[self.num_of_dishes] = dish
        return self.num_of_dishes

    def delete_dish_by_idx(self, idx):
        dish = self.dishes.pop(idx)  # removing the dish from the DishesCollection
        meals_col.remove_dish(idx)
        del dish  # removing the deleted dish from memory

    def get_dish_idx_by_name(self, name):
        dish = self.get_dish_by_name(name)
        return dish._get_idx()


dishes_collection = DishesCollection()  # Global dishes collection

class Dishes(Resource):
    """A Class implementing a REST API for dealing with Dishes"""

    def get(self):
        return parse_cursor(dishes_col.find())

    def post(self):
        # TODO: verify the JSON header. return 0 and status 415 (slide 13)
        print("Adding a dish")
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        args = parser.parse_args()
        dish_name = args['name']
        print(f"Dish name to add: {dish_name}")
        if dish_name is None: 
            return -1, 422

        # Checking if the Dish already exists in the DB
        dish = dishes_col.find_one({'name': dish_name})
        if dish is not None:
            return -2, 422  # TODO: verify that this is the correct return code

        try:
            # idx = dishes_collection.add_dish(dish_name)
            # TODO: make sure we refer to the right variable '_id'

            # Getting the index of current dish
            idx = counters_col.find_one({"_id": 0})["dishes"]
            print(f"Creating a dish object")
            dish = Dish(dish_name, idx)
            dish_dict = dish.get_as_dict()
            print(f"Adding the following to DB: {dish_dict}")
            # TODO: probably pass dish_dict instead of the dict below
            result = dishes_col.insert_one(dish_dict)
            # result = dishes_col.insert_one({"_id": idx, "name": dish_name})
            print(f"added the {dish_name} dish as index {idx}")
            counters_col.update_one({"_id": 0}, {"$set": {'dishes': idx + 1}})
            print(f"Updated the index")
        except ValueError:
            return -3, 422
        except Exception as e:  # Specify Exception type
            print(type(e), e)
            traceback.print_exc()
            return -4, 504
        return idx, 201

    def delete(self):  # Can we simply remove this and get the same functionality?
        return "This method is not allowed for the requested URL", 405


'''
class Dishes(Resource):
    """A Class implementing a REST API for dealing with Dishes"""

    def get(self):
        return dishes_collection._get_all_dishes(), 200

    def post(self):
        # TODO: verify the JSON header. return 0 and status 415 (slide 13)
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        args = parser.parse_args()
        dish_name = args['name']
        if dish_name is None: 
            return -1, 422
        if dishes_collection.dish_exists(dish_name):
            return -2, 422  # Dish name already exists
        try:
            idx = dishes_collection.add_dish(dish_name)
        except ValueError:
            return -3, 422
        except Exception:  # Specify Exception type
            return -4, 504
        return idx, 201

    def delete(self):  # Can we simply remove this and get the same functionality?
        return "This method is not allowed for the requested URL", 405
'''


class DishesId(Resource):
    """RESTful API for dealing with dishes/id resources"""

    def get(self, idx):
        print(f"Getting a dish by index {idx}")
        idx = int(idx)
        try:
            dish = dishes_col.find_one({'ID': idx})
            del dish['_id']
            return dish
            # return dishes_collection.get_dish_by_idx(idx).get_as_dict(), 200  # TODO: remove line
        except KeyError:
            return -5, 404

    def delete(self, idx):
        idx = int(idx)
        try:
            deleted = dishes_col.delete_one({'ID': idx})
            if deleted != 1:
                print(f"WARNING: When deleting index {idx} {deleted.deleted_count} items were deleted!")
            # dishes_collection.delete_dish_by_idx(idx)
            return idx, 200
        except KeyError:
            return -5, 404


class DishesName(Resource):
    """RESTful API for dealing with dishes/name resources"""

    def get(self, name):
        try:
            dish = dishes_col.find_one({'name': name})
            del dish['_id']
            return dish
            #return dishes_collection.get_dish_by_name(name).get_as_dict()  # TODO: Add response value
        except ValueError as e:
            print(str(e))
            return -5, 404

    def delete(self, name):
        try:
            dish = self.get(name)
            print(f"Got a dish: {dish}")
            idx = dish['ID']
            
            deleted = dishes_col.delete_one({'ID': idx})
            if deleted != 1:
                print(f"WARNING: When deleting index {idx} {deleted.deleted_count} items were deleted!")
            ''''
            dish = dishes_collection.get_dish_by_name(name)
            idx = dish._get_idx()
            dishes_collection.delete_dish_by_idx(idx)
            '''
            return idx, 200
        except ValueError:
            return -5, 404


class Meal:
    """Class representing a Meal consisting of appetizer, main and dessert"""

    def __init__(self, name, idx, appetizer, main, dessert):
        self.name = name
        self.idx = idx
        self.appetizer = appetizer
        self.main = main
        self.dessert = dessert
        self.update_nutritional_vals()

    def update_nutritional_vals(self):
        self.cal = 0
        self.sugar = 0
        self.sodium = 0
        for dish_idx in [self.appetizer, self.main, self.dessert]:
            if dish_idx is None:
                print("Skipping dish nutritional values")
                continue
            try:
                #dish = dishes_collection.get_dish_by_idx(dish_idx)
                dish = dishes_col.find_one({'ID': dish_idx})
                self.cal += dish['cal']
                self.sugar += dish['sugar']
                self.sodium += dish['sodium']
            except Exception as e:  # Narrow down exception type
                raise e

    def get_name(self):
        return self.name

    def get_idx(self):
        return self.idx

    def get_as_dict(self):
        return {'name': self.get_name(), 'ID': self.get_idx(), 'appetizer': self.appetizer, 'main': self.main, 'dessert': self.dessert, 'cal': self.cal, 'sodium': self.sodium, 'sugar': self.sugar}

    def update(self, name, appetizer, main, dessert):
        print(f"Updating dish from {self.name} {self.appetizer} {self.main} {self.dessert} to {name} {appetizer} {main} {dessert} ")
        self.name = name
        self.appetizer = appetizer
        self.main = main
        self.dessert = dessert
        self.update_nutritional_vals()

    def remove_dish(self, idx):
        if self.appetizer == idx:
            print(f"Removing appetizer from meal! (idx: {idx})")
            self.appetizer = None
        if self.main == idx:
            print(f"Removing main from meal! (idx: {idx})")
            self.main = None
        if self.dessert == idx:
            print(f"Removing dessert from meal! (idx: {idx})")
            self.dessert = None
        self.update_nutritional_vals()


class MealsCollection:
    """Class representing a collection of meals"""

    def __init__(self):
        self.num_of_meals = 0
        self.meals = dict()

    def add_meal(self, name, appetizer, main, dessert):
        self.num_of_meals += 1  # No concurrency support.  # TODO: failing to create a meal with result in an unused idx
        meal = Meal(name, self.num_of_meals, appetizer, main, dessert)
        self.meals[self.num_of_meals] = meal
        return self.num_of_meals  # The index of the meal

    def get_all_meals(self):
        meals_json = {idx: meal.get_as_dict() for idx, meal in self.meals.items()}
        return meals_json

    def get_meal_by_idx(self, idx):
        return self.meals[idx]

    def get_meal_by_name(self, name):
        print(f"Looking for meal named {name} in {len(self.meals.keys())} meals..")
        for _, meal in self.meals.items():  # TODO: Use .values() instead of .items()
            if meal.get_name() == name:
                return meal
        raise ValueError(f"Couldn't find a meal named {name}")

    def delete_meal_by_idx(self, idx):
        meal = self.meals.pop(idx)
        del meal

    def delete_meal_by_name(self, name):
        meal = self.get_meal_by_name(name)
        idx = meal.get_idx()
        del self.meals[idx]
        return idx

    def remove_dish(self, idx):
        for meal in self.meals.values():
            meal.remove_dish(idx)


#meals_col = MealsCollection()


class Meals(Resource):
    """RESTful API for the meals resource"""

    def post(self):
        print(f"meals post invoke")
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('appetizer', required=True, type=int)
        parser.add_argument('main', required=True, type=int)
        parser.add_argument('dessert', required=True, type=int)
        args = parser.parse_args()
        print(args)
        try:
            name = args['name']
            appetizer = args['appetizer']
            main = args['main']
            dessert = args['dessert']
            print('get index')
            idx = counters_col.find_one({"_id": 0})["meals"]
            print('making meal')
            meal = Meal(name=name, appetizer=appetizer, main=main, dessert=dessert, idx=idx)
            meal_dict = meal.get_as_dict()
            print(f"Adding a meal. Name: {name}, appetizer: {appetizer}, main: {main} dessert: {dessert}")
            # print(dishes_collection._get_all_dishes())
            result = meals_col.insert_one(meal_dict)
            print(f"added the {name} dish as index {idx}")
            counters_col.update_one({"_id": 0}, {"$set": {'meals': idx + 1}})
            #meals_col.insert_one({'name': name, 'appetizer': appetizer, 'main': main, 'dessert': dessert})
            return idx, 201
        except KeyError as e:
            print(f"Invalid key: {e}")
            #traceback.print_exc()
            return -6, 422

    def get(self):
        print(f"Getting all meals")
        meals = parse_cursor(meals_col.find())
        return meals, 200



class MealsId(Resource):
    """Class for the REST API of means/name"""

    def get(self, idx):  # TODO: Add failure. reponse -5, code 404
        idx = int(idx)
        print('MealsId Get invoked')
        print(type(idx))
        try:
            meal = meals_col.find_one({'ID': idx})
            del meal['_id']# TODO: Except KeyError
            print(f"Retrieved a meal by the meals/id resource for idx {idx}: {meal}")
            return meal, 200
        except KeyError:
            return -5, 404

    def delete(self, idx):  # TODO: Add failure. reponse -5, code 404
        try:
            deleted = meals_col.delete_one({'ID': idx})
            if deleted != 1:
                print(f"WARNING: When deleting index {idx} {deleted.deleted_count} items were deleted!")
            else:
                print('deleted successfully')
            return idx, 200
        except KeyError:
            return -5, 404

    def put(self, idx):
        idx = int(idx)
        print(f"meals/id/put invoked")
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('appetizer', required=True, type=int)
        parser.add_argument('main', required=True, type=int)
        parser.add_argument('dessert', required=True, type=int)
        args = parser.parse_args()
        print(args)
        try:
            name = args['name']
            appetizer = args['appetizer']
            main = args['main']
            dessert = args['dessert']
            print(f"Updating a meal. Name: {name}, idx: {idx}, appetizer: {appetizer}, dessert: {dessert}")
            #below meal for debugging only
            meal = meals_col.find_one({'ID': idx})
            print(meal)
            # del meal['_id']
            meal = Meal(name=name, appetizer=appetizer, main=main, dessert=dessert, idx=idx).get_as_dict()
            del meal['ID']
            meals_col.update_one({'ID': idx}, {"$set": meal})
            print(meals_col.find_one({'ID': idx}))
            return idx, 200
        except KeyError as e:  # TODO: What errors may we catch here? How to handle them?
            print(f"Invalid key: {e}")
            return -6, 422  # Verify this is correct for the `put` API


class MealsName(Resource):
    """Class for the REST API of means/name"""

    def get(self, name):  # TODO: Add failure. reponse -5, code 404
        try:
            meal = meals_col.find_one({'name': name})
            del meal['_id']
            print(f"Retrieved a meal by the meals/name resource for name {name}: {meal}")
            return meal, 200
        except ValueError:
            return -5, 404

    def delete(self, name):  # TODO: Add failure. reponse -5, code 404
        try:
            deleted = meals_col.delete_one({'name': name})
            if deleted != 1:
                print(f"WARNING: When deleting name {name} {deleted.deleted_count} items were deleted")
            return name, 200
        except ValueError:
            return -5, 404

# Adding resources to the Flask app API
api.add_resource(Dishes, '/dishes')
api.add_resource(DishesId, '/dishes/<int:idx>')
api.add_resource(DishesName, '/dishes/<string:name>')
api.add_resource(Meals, '/meals')
api.add_resource(MealsId, '/meals/<int:idx>')
api.add_resource(MealsName, '/meals/<string:name>')

# if __name__ == '__main__':
#     print(f"Running Meals&Dishes server ({__file__})")
#     app.run(host='http://127.0.0.1', port=5001, debug=True)

