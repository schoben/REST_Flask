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


# Setting up global variables
# TODO: extract to a function
app = Flask(__name__)  # initialize Flask
api = Api(app)  # create API
# ninja_api_key = os.environ['NINJA_API_KEY']
client = pymongo.MongoClient("localhost", 27017)

# initializing the database
db = client["food"]
dishes_col = db["dishes"]  # TODO: dish the dish
meals_col = db["meals"]
diets_col = db["diets"]
counters_col = db["counter"]

# Resetting database
print(f"WARNING: Restting collections!")
dishes_col.drop()
meals_col.drop()
diets_col.drop()
counters_col.drop()

# print('readding schema')
# db = client["food"]
# dishes_col = db["dishes"]  # TODO: dish the dish
# meals_col = db["meals"]
# diets_col = db["diets"]
# counters_col = db["counter"]