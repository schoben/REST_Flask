"""
Exercise 1# for Cloud Computing course
Creating a server docker image implementing a REST API
"""

# Built-in imports
import os
from collections import namedtuple
import flask
# pip imports
from flask import Flask  # , jsonify
from flask_restful import Resource, Api, reqparse
import requests
import pymongo
import traceback

HEADERS = ('Content-Type', 'application/json')
# Setting up global variables
# TODO: extract to a function
app = Flask(__name__)  # initialize Flask
api = Api(app)  # create API
ninja_api_key = 'GZhBLJkOriPZwhCOJlOdHg==UEeUzdzoKypBxfto'
    #os.environ['NINJA_API_KEY']
client = pymongo.MongoClient("mongodb://mongo:27017")
# client = pymongo.MongoClient('localhost', 27017)

# initializing the database
db = client["food"]
dishes_col = db["dishes"]
meals_col = db["meals"]
# diets_col = db["diets"]
counters_col = db["counter"]
DIETS = 'diets'
PORT = 80
RESOURCE = 'diets'

# TODO export to a function
# Initializing counters
counters = counters_col.find_one({'_id': 0})
if counters is None:
    print("Couldn't find any counters! Initializing counters to 0")
    counters_col.insert_one({'_id': 0, 'dishes': 0, 'meals': 0})
else:
    print(f"Found counters: {counters}")


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
    print(parsed_dict)
    for d in parsed_dict:
        del d['_id']
    return parsed_dict


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


class Dishes(Resource):
    """A Class implementing a REST API for dealing with Dishes"""

    def get(self):
        return parse_cursor(dishes_col.find())

    def post(self):
        # TODO: verify the JSON header. return 0 and status 415 (slide 13)
        if HEADERS not in flask.request.headers.items():
            return 0, 415
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
            # Getting the index of current dish
            idx = counters_col.find_one({"_id": 0})["dishes"]
            print(f"Creating a dish object")
            dish = Dish(dish_name, idx)
            dish_dict = dish.get_as_dict()
            print(f"Adding the following to DB: {dish_dict}")
            result = dishes_col.insert_one(dish_dict)
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


class DishesId(Resource):
    """RESTful API for dealing with dishes/id resources"""

    def get(self, idx):
        print(f"Getting a dish by index {idx}")
        idx = int(idx)
        dish = dishes_col.find_one({'ID': idx})
        if dish is None:
            return -5, 404
        del dish['_id']
        return dish

    def delete(self, idx):
        idx = int(idx)
        deleted = dishes_col.delete_one({'ID': idx})
        if deleted.deleted_count == 0:
            print(f"WARNING: When deleting index {idx} {deleted.deleted_count} items were deleted!")
            return -5, 404
        update_deleted_dish(idx)
        return idx, 200



def update_deleted_dish(idx):
    meals = meals_col.find()
    meals = list(meals)
    for meal in meals:
        appetizer = meal['appetizer'] if meal['appetizer'] != idx else None
        main = meal['main'] if meal['main'] != idx else None
        dessert = meal['dessert'] if meal['dessert'] != idx else None
        meal_obj = Meal(meal['name'], meal['ID'], appetizer, main, dessert)
        meals_col.update_one({'ID': meal['ID']}, {'$set': meal_obj.get_as_dict()})


class DishesName(Resource):
    """RESTful API for dealing with dishes/name resources"""

    def get(self, name):
        dish = dishes_col.find_one({'name': name})
        if dish is None:
            return -5, 404
        del dish['_id']
        return dish

    def delete(self, name):
        try:
            dish = self.get(name)
            if isinstance(dish, tuple):
                return dish  # HACK: the 'dish' here is in fact the desired response.
            print(f"Got a dish: {dish}")
            idx = dish['ID']
            
            deleted = dishes_col.delete_one({'ID': idx})
            if deleted != 1:
                print(f"WARNING: When deleting index {idx} {deleted.deleted_count} items were deleted!")
            update_deleted_dish(idx)
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


class Meals(Resource):
    """RESTful API for the meals resource"""

    def post(self):
        if HEADERS not in flask.request.headers.items():
            return 0, 415
        print(f"meals post invoke")
        parser = reqparse.RequestParser()
        try:
            parser.add_argument('name', required=True)
            parser.add_argument('appetizer', required=True, type=int)
            parser.add_argument('main', required=True, type=int)
            parser.add_argument('dessert', required=True, type=int)
            args = parser.parse_args()
            print(args)
        except Exception as e:  # narrow down type
            return -1, 422
        try:
            name = args['name']
            meals = meals_col.find_one({'name': name})
            if meals is not None:
                return -2, 422
            appetizer = args['appetizer']
            main = args['main']
            dessert = args['dessert']
            idx = counters_col.find_one({"_id": 0})["meals"]
            print(idx)
            print('making meal')
            meal = Meal(name=name, appetizer=appetizer, main=main, dessert=dessert, idx=idx)
            meal_dict = meal.get_as_dict()
            print(f"Adding a meal. Name: {name}, appetizer: {appetizer}, main: {main} dessert: {dessert}")
            result = meals_col.insert_one(meal_dict)
            print(f"added the {name} dish as index {idx}")
            counters_col.update_one({"_id": 0}, {"$set": {'meals': idx + 1}})
            return idx, 201
        except KeyError as e:
            print(f"Invalid key: {e}")
            # traceback.print_exc()
            return -6, 422

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('diet', type=str, location='args', required=False)
        args = parser.parse_args()
        if args['diet']:
            diet = args['diet']
            res = requests.get(f'http://{DIETS}:{PORT}/{RESOURCE}/{diet}')
            if not res:
                return f'Diet {diet} not found', 404
            diet_dict = res.json()
            relevant_meals = []
            all_meals = parse_cursor(meals_col.find())
            for meal in all_meals:
                if meal['cal'] <= diet_dict['cal'] and meal['sodium'] <= diet_dict['sodium'] \
                        and meal['sugar'] <= diet_dict['sugar']:
                    relevant_meals.append(meal)
            #assuming under the values
            return relevant_meals, 200
        else:
            print(f"Getting all meals")
            meals = parse_cursor(meals_col.find())
            return meals, 200




class MealsId(Resource):
    """Class for the REST API of means/name"""

    def get(self, idx):
        idx = int(idx)
        print('MealsId Get invoked')
        print(type(idx))
        meal = meals_col.find_one({'ID': idx})
        if meal is None:
            return -5, 404
        del meal['_id']
        print(f"Retrieved a meal by the meals/id resource for idx {idx}: {meal}")
        return meal, 200

    def delete(self, idx):
        try:
            deleted = meals_col.delete_one({'ID': idx})
            if deleted.deleted_count == 0:
                print(f"WARNING: When deleting index {idx} {deleted.deleted_count} items were deleted!")
                return -5, 404
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
            meal = meals_col.find_one({'ID': idx})
            if meal is None:
                return -5, 404
            print(meal)
            meal = Meal(name=name, appetizer=appetizer, main=main, dessert=dessert, idx=idx).get_as_dict()
            del meal['ID']
            meals_col.update_one({'ID': idx}, {"$set": meal})
            print(meals_col.find_one({'ID': idx}))
            return idx, 200
        except KeyError as e:
            print(f"Invalid key: {e}")
            return -6, 422
        except Exception as e:
            return -6, 422


class MealsName(Resource):
    """Class for the REST API of means/name"""

    def get(self, name):
        meal = meals_col.find_one({'name': name})
        if meal is None:
            return -5, 404
        del meal['_id']
        print(f"Retrieved a meal by the meals/name resource for name {name}: {meal}")
        return meal, 200

    def delete(self, name):
        try:
            meal = meals_col.find_one({'name': name})
            if meal is None:
                return -5, 404
            idx = meal['ID']
            deleted = meals_col.delete_one({'name': name})
            if deleted.deleted_count == 0:
                print(f"WARNING: When deleting name {name} {deleted.deleted_count} items were deleted")
                return -5, 404
            return idx, 200
        except ValueError:
            return -5, 404

# Adding resources to the Flask app API
api.add_resource(Dishes, '/dishes')
api.add_resource(DishesId, '/dishes/<int:idx>')
api.add_resource(DishesName, '/dishes/<string:name>')
api.add_resource(Meals, '/meals')
api.add_resource(MealsId, '/meals/<int:idx>')
api.add_resource(MealsName, '/meals/<string:name>')

if __name__ == '__main__':
    print(f"Running Meals&Dishes server ({__file__})")
    # app.run(host='http://127.0.0.1', port=5001, debug=True)

