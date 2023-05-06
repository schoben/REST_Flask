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

# Setting up global variables
app = Flask(__name__)  # initialize Flask
api = Api(app)  # create API
ninja_api_key = os.environ['NINJA_API_KEY']

# Creating a namedtuple for storing dish values
DishValues = namedtuple('DishValues', ['size', 'cal', 'sugar', 'sodium'])


# TODO: move following two function to a different module. Consider encapsulating in a class
def query_ninja(query):  # TODO: Deal with failures (no connection, unrecognized)
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(query)
        response = requests.get(api_url, headers={'X-Api-Key': ninja_api_key})
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

    def get_as_dict(self):
        return {'name': self.name, 'id': self.idx, 'cal': self.cal, 'size': self.size, 'sodium': self.sodium, 'sugar': self.sugar}



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
        try:
            self.get_dish_by_name(name)
            return True
        except ValueError:
            return False

    def add_dish(self, name):
        self.num_of_dishes += 1  # No support for concurrency
        print(f"Adding to Dishes: name {name}, idx: {self.num_of_dishes}")
        dish = Dish(name, self.num_of_dishes)
        self.dishes[self.num_of_dishes] = dish
        return self.num_of_dishes

    def delete_dish_by_idx(self, idx):
        dish = self.dishes.pop(idx)  # removing the dish from the DishesCollection
        del dish  # removing the deleted dish from memory

    def get_dish_idx_by_name(self, name):
        dish = self.get_dish_by_name(name)
        return dish._get_idx()


dishes_collection = DishesCollection()  # Global dishes collection


class Dishes(Resource):
    """A Class implementing a REST API for dealing with Dishes"""

    def get(self):
        return dishes_collection._get_all_dishes(), 200

    def post(self):
        # TODO: verify the JSON header. return 0 and status 415 (slide 13)
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='args', required=True)  # location='args' is required, at least on macOS
        args = parser.parse_args()
        try:
            dish_name = args['name']
        except KeyError:
            return -1, 422  # No dish name supplied
        if dishes_collection.dish_exists(dish_name):
            return -2, 422  # Dish name already exists
        try:
            idx = dishes_collection.add_dish(dish_name)
        except Exception:  # Split to two types of exceptions
            # Not recognized: return -3, status 400 (slide 15)
            # Unreachable: return -4, status 504
            raise NotImplementedError("Unexpected error (ninja?)")
        return idx, 201

    def delete(self):  # Can we simply remove this and get the same functionality?
        return "This method is not allowed for the requested URL", 405



class DishesId(Resource):
    """RESTful API for dealing with dishes/id resources"""

    def get(self, idx):
        try:
            return dishes_collection.get_dish_by_idx(idx).get_as_dict(), 200
        except KeyError:
            return -5, 404

    def delete(self, idx):
        try:
            dishes_collection.delete_dish_by_idx(idx)
            return idx, 200
        except KeyError:
            return  -5, 404


class DishesName(Resource):
    """RESTful API for dealing with dishes/name resources"""

    def get(self, name):
        try:
            return dishes_collection.get_dish_by_name(name).get_as_dict()  # TODO: Add response value
        except ValueError as e:
            print(str(e))
            return -5, 404

    def delete(self, name):
        try:
            dish = dishes_collection.get_dish_by_name(name)
            idx = dish._get_idx()
            dishes_collection.delete_dish_by_idx(idx)
            return idx, 200
        except ValueError:
            return  -5, 404


class Meal:
    """Class representing a Meal consisting of appetizer, main and dessert"""

    def __init__(self, name, idx, appetizer, main, dessert):
        self.name = name
        self.idx = idx
        self.appetizer = appetizer  # Using idx instead of obj: dishes_collection.get_dish_by_idx(appetizer)
        self.main = main  # Using idx instead of obj: dishes_collection.get_dish_by_idx(main)
        self.dessert = dessert  # Using idx instead of obj: dishes_collection.get_dish_by_idx(dessert)

    def get_name(self):
        return self.name

    def get_idx(self):
        return self.idx

    def get_as_dict(self):
        return {'name': self.get_name(), 'ID': self.get_idx(), 'appetizer': self.appetizer, 'main': self.main, 'dessert': self.dessert, 'cal': 9, 'sodium': 9, 'sugar': 9}


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


meals_collection = MealsCollection()


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
            print(f"Adding a meal. Name: {name}, appetizer: {appetizer}, dessert: {dessert}")
            print(dishes_collection._get_all_dishes())
            idx = meals_collection.add_meal(name, appetizer, main, dessert)
            return idx, 201
        except KeyError as e:
            print(f"Invalid key: {e}")
            return -6, 422

    def get(self):
        print(f"Getting all meals")
        meals = meals_collection.get_all_meals()
        return meals, 200


class MealsId(Resource):
    """Class for the REST API of means/name"""

    def get(self, idx):
        meal = meals_collection.get_meal_by_idx(idx).get_as_dict()  # TODO: Except KeyError
        print(f"Retrieved a meal by the meals/id resource for idx {idx}: {meal}")
        return meal, 200

    def delete(self, idx):
        meals_collection.delete_meal_by_idx(idx)
        return idx, 200

    def put(self, idx):
        raise NotImplementedError  # TODO: Should return status 200


class MealsName(Resource):
    """Class for the REST API of means/name"""

    def get(self, name):
        meal = meals_collection.get_meal_by_name(name).get_as_dict()
        print(f"Retrieved a meal by the meals/name resource for name {name}: {meal}")
        return meal, 200

    def delete(self, name):
        idx = meals_collection.delete_meal_by_name(name)  # TODO: Except ----
        return idx, 200


# Adding resources to the Flask app API
api.add_resource(Dishes, '/dishes')
api.add_resource(DishesId, '/dishes/<int:idx>')
api.add_resource(DishesName, '/dishes/<string:name>')
api.add_resource(Meals, '/meals')
api.add_resource(MealsId, '/meals/<int:idx>')
api.add_resource(MealsName, '/meals/<string:name>')

if __name__ == '__main__':
    print(f"Running Meals&Dishes server ({__file__})")
    app.run(port=5002)  # TODO: read port from cfg/argsparser

