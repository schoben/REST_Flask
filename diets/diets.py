import os

# pip imports
import flask
from flask import Flask  # , jsonify
from flask_restful import Resource, Api, reqparse
import requests
import pymongo
import traceback


# Setting up global variables
# TODO: extract to a function
app = Flask(__name__)  # initialize Flask
api = Api(app)  # create API


client = pymongo.MongoClient("mongodb://mongo:27017/")
db = client["food"]
diets_col = db["diets"]


FIELDS = ['name', 'cal', 'sodium', 'sugar']
HEADERS = ('Content-Type', 'application/json')


def parse_cursor(cursor):
    parsed_dict = list(cursor)
    for d in parsed_dict:
        del d['_id']
    return parsed_dict


class Diets(Resource):
    """RESTful API for the meals resource"""

    def post(self):
        print(f"diets post invoke")
        parser = reqparse.RequestParser()
        try:
            parser.add_argument('name', required=True)
            parser.add_argument('cal', required=True, type=int)
            parser.add_argument('sodium', required=True, type=int)
            parser.add_argument('sugar', required=True, type=int)
            args = parser.parse_args()
            print(args)
        except Exception as e:
            print(f"Invalid key: {e}")
            return 'Incorrect POST format', 422
        if HEADERS not in flask.request.headers.items():
            return f'POST expects content type to be application/json', 415
        name = args['name']
        cal = args['cal']
        sodium = args['sodium']
        sugar = args['sugar']
        print(f"Adding a diet Name: {name}")
        diet = diets_col.find_one({'name': name})
        if diet is not None:
            return f"Diet with {name} already exists", 422  # TODO: verify that this is the correct return code
        diet_dict = {k: v for k, v in zip(FIELDS, [name, cal, sodium, sugar])}
        diets_col.insert_one(diet_dict)
        return f'Diet {name} was created successfully', 201


    def get(self):
        print(f"Getting all meals")
        diets = parse_cursor(diets_col.find())
        return diets, 200


class DietsName(Resource):
    """RESTful API for dealing with dishes/name resources"""

    def get(self, name):
        # try:
        diet = diets_col.find_one({'name': name})
        if not diet:
            return f'Diet {name} not found', 404
        del diet['_id']
        return diet, 200
            # return dishes_collection.get_dish_by_name(name).get_as_dict()  # TODO: Add response value
        # except ValueError as e:
        #     print(str(e))
        #     return f'Diet {name} not found', 404

    # def delete(self, name):
    #     try:
    #         dish = self.get(name)
    #         print(f"Got a dish: {dish}")
    #         idx = dish['id']
    #
    #         deleted = diets_col.delete_one({'id': idx})
    #         if deleted != 1:
    #             print(f"WARNING: When deleting index {idx} {deleted.deleted_count} items were deleted!")
    #         ''''
    #         dish = dishes_collection.get_dish_by_name(name)
    #         idx = dish._get_idx()
    #         dishes_collection.delete_dish_by_idx(idx)
    #         '''
    #         return idx, 200
    #     except ValueError:
    #         return -5, 404
    #
api.add_resource(Diets, '/diets')
api.add_resource(DietsName, '/diets/<string:name>')

if __name__ == '__main__':
    print(f"Running Diets server ({__file__})")
#     app.run(host='0.0.0.0', port=5002, debug=True)