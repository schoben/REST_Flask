"""
Client module for testing
"""


import requests
import json


# Sources paths
port = '8000'
root = 'http://127.0.0.1:' + port
dishes = root + '/dishes'
header = {'Content-Type': 'application/json'}


# Function for communicating with server
def get_all_dishes():
    return requests.get(dishes)


def post_dish(name):
    return requests.post(dishes, headers=header, data=json.dumps({'name': name}))


def get_dish_by_name(name):  # TODO: remove this or previous func
    return requests.get(dishes + '/' + name)


def delete_dish_by_name(name: str):
    return requests.delete(dishes + '/' + name)


def get_dish_by_idx(idx):
    return requests.get(dishes + '/' + idx)


def delete_dish_by_idx(idx):
    return requests.delete(dishes + '/' + idx)


# Verification functions
def print_res(res):
    print(res.json(), res)
    print()


def verify_res_json(res, json):
    assert res.json() == json


def verify_res_code(res, code):
    assert res.status_code == code


def verify_res(res, json, code):
    verify_res_json(res, json)
    verify_res_code(res, code)


# Dishes Tests

print(f"Test 1#: Adding a 'fish' dish. Should return 1 (index of the dish) with code 201")
res = post_dish('fish')
print_res(res)
verify_res_code(res, 201)


print(f"Test 2#: Adding a 'mish' dish. Should return 1 (index of the dish) with code 201")
res = post_dish('mish')
print_res(res)
verify_res_code(res, 201)


print(f"Test 3#: getting all dishes. Should return empty dict")
res = get_all_dishes()
print_res(res)
verify_res_code(res, 200)

print(f"Test 4#: Adding a 'mish' dish again. Should return -2 with code ?")
res = post_dish('mish')
print_res(res)
# verify_res_code(res, 201)

'''
print(f"Test 3#: Deleting the whole dishes resource. Should give an error with code 405")
res = requests.delete(dishes)
print_res(res)
verify_res_code(res, 405)


print(f"Test 4#: Getting dish of index 1. Should return the 'fish' dish")
res = get_dish_by_idx('1')
print_res(res)
verify_res_code(res, 200)


print(f"Test 5#: Getting dish 'fish'. Should return the 'fish' dish")
res = get_dish_by_name('fish')
print_res(res)
verify_res_code(res, 200)


print(f"Test 6#: Getting dish of index 2. Should return -5 with code 404")
res = get_dish_by_idx('2')
print_res(res)
verify_res_code(res, 404)
assert res.text.rstrip() == "-5"  # TODO: why do we need rstrip? Why do we have a linebreak in the reponse?


print(f"Test 7#: Getting a dish 'phish'. Should return -5 with status 404.")
res = get_dish_by_name('phish')
print_res(res)
verify_res_code(res, 404)
assert res.text.rstrip() == '-5'


print(f"Test 8#: Deleting a dish of index 1. Should return code 200 and value 1 (the index of fish)")
res = delete_dish_by_idx('1')
print_res(res)
verify_res_code(res, 200)
assert res.text.rstrip() == '1'


print("Dish list should now be empty")
res = get_all_dishes()
print_res(res)
verify_res_code(res, 200)


print(f"Test 9#: Adding and deleting a dish 'chicken'. Should return code 200 and value 2 (the index of chicken)")
post_dish('chicken')
res = delete_dish_by_name('chicken')
print_res(res)
verify_res_code(res, 200)
assert res.text.rstrip() == '2'


print(f"Test 10#: Deleting a dish of index 3. Should return -5 with status 404.")
response = delete_dish_by_idx('3')
print_res(response)
verify_res_code(response, 404)
assert response.text.rstrip() == '-5'


print(f"Test 11#: Deleting a dish 'phish'. Should return -5 with status 404.")
response = delete_dish_by_name('phish')
print_res(response)
verify_res_code(response, 404)
assert response.text.rstrip() == '-5'





# Tests for Meals

post_dish('salad')
post_dish('steak')
post_dish('ice cream')
print(f"Printing all existing dishes at this point:")
print_res(get_all_dishes())


# Adding a first meal
print(f"Adding a meal. Should return 1")
meals = root + '/meals'
header = {'Content-Type': 'application/json'}
basic_meal = json.dumps({'name': 'basic', 'appetizer': 3, 'main': 4, 'dessert': 5})
res = requests.post(meals, headers=header, data=basic_meal)
print_res(res)


# Test: Getting all meals. Should have a single 'basic' meal.
def get_all_meals():
    return requests.get(meals, headers=header)


print(f"Printing all available meals:")
res = get_all_meals()
print(res.json())
print()


def get_meal(identifier):
    return requests.get(meals + '/' + identifier)

def delete_meal(identifier):
    return requests.delete(meals + '/' + identifier)


# Getting a meal by index
print(f"Getting meal of index 1")
res = get_meal('1')
print_res(res)
print()


# Getting a meal by name
print(f"Getting meal by name 'basic'")
res = get_meal('basic')
print_res(res)
print()


# Delete meal by index
print(f"Deleteing meal of index 1")
res = delete_meal('1')
print_res(res)
print()


print(f"Adding a bread dish")
res = post_dish('bread')
print_res(res)
print()


print("Adding a hamburger dish")
res = post_dish('hamburger')
print_res(res)
print()

print("Adding a souffle dish")
res = post_dish('souffle')
print_res(res)
print()


alt_dish = json.dumps({'name': 'alt', 'appetizer': 6, 'main': 7, 'dessert': 8})
print(f"Adding an 'alt' meal: {alt_dish}")
res = requests.post(meals, headers=header, data=alt_dish)
print_res(res)
print()


# List meals
print(f"Listing all available meals. Should contain an 'alt' meal only.")
res = get_all_meals()
print(res.json())
print()


# Add and delete a meal by name
print(f"Deleting an 'alt' meal. Should return 2 (index of 'alt' meal)")
res = delete_meal('alt')
print_res(res)
print()


# Test for getting a meal with invalid id
print(f"Testing meals/get on invalid index. Should return -5 and code 404")
res = get_meal('7')
print_res(res)
print()


# Test for getting a meal with invalid name
print(f"Testing meals/get on invalid name. Should return -5 and code 404")
res = get_meal('Italian Monday')
print_res(res)
print()


# Test for getting a meal with invalid id
print(f"Testing meals/get on invalid index. Should return -5 and code 404")
res = delete_meal('7')
print_res(res)
print()


# Test for getting a meal with invalid name
print(f"Testing meals/get on invalid name. Should return -5 and code 404")
res = delete_meal('Italian Monday')
print_res(res)
print()


# re-adding 'basic' meal
print(f"Adding the 'basic' meal again")
res = requests.post(meals, headers=header, data=basic_meal)


# List meals
print(f"Listing all available meals:")
res = get_all_meals()
print(res.json())
print()


def update_meal(idx, name, appetizer, main, dessert):
    load = json.dumps({'name': name, 'appetizer': appetizer, 'main': main, 'dessert': dessert})
    return requests.put(meals + '/' + idx, headers=header, data=load)


# Updating an existing meal with put
print(f"Updating the 'basic' meal")
res = update_meal('3', 'basic_updated', 3, 4, 8)
print_res(res)
print()


print(f"Printing all available meals")
res = get_all_meals()
print_res(res)
print()
res = requests.post(meals, headers=header, data=basic_meal)


# Updating an invalid meal with put
print(f"Updating a non-existing meal")
res = update_meal('7', 'basic_updated', 3, 4, 8)
print_res(res)
print()

print(f"Adding a dish")
res = post_dish("focaccia")
print_res(res)
print()

print(f"Getting the souffle dish")
res = get_dish_by_name("souffle")
print_res(res)
print()

print(f"Deleting a dish that is already a part of a meal")

print(f"We delete the dessert of the 'basic_updated' meal")
res = get_meal('basic_updated')
print_res(res)
print()

print(f"We now delete dish with index 8")
res = delete_dish_by_idx('8')
print_res(res)
print()

print(f"Let's see how this affected the meal:")
res = get_meal('basic_updated')
print_res(res)
print()
'''

