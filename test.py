"""
Client module for testing

TODO:
* Typing
"""


import requests
import json


# Sources paths
root = 'http://127.0.0.1:5002'
dishes = root + '/dishes'


# Function for communicating with server
def get_all_dishes():
    return requests.get(dishes)


def post_dish(name):
    return requests.post(dishes, params={'name': name})


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





# Tests

print(f"Test 1#: getting all dishes. Should return empty dict")
res = get_all_dishes()
print_res(res)
verify_res_code(res, 200)


print(f"Test 2#: Adding a 'fish' dish. Should return 1 (index of the dish) with code 201")
res = post_dish('fish')
print_res(res)
verify_res_code(res, 201)


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


print(f"Test 9#: Adding and deleting a dish 'chicken'. Should return code 200 and value 2 (the index of chicken)")
post_dish('chicken')
res = delete_dish_by_name('chicken')
print_res(res)
verify_res_code(res, 200)
assert res.text.rstrip() == '2'


print(f"Test 10#: Dleting a dish of index 3. Should return -5 with status 404.")
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
print_res(get_all_dishes())


meals = root + '/meals'
header = {'Content-Type': 'application/json'}
payload = json.dumps({'name': 'basic', 'appetizer': 3, 'main': 4, 'dessert': 5})
res = requests.post(meals, headers=header, data=payload)
print_res(res)

res = requests.get(meals, headers=header)
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


# Add and delete a meal by name
print(f"Adding and deleting an 'alt' meal")
post_dish('bread')
post_dish('steak')
post_dish('souffle')
alt_dish = json.dumps({'name': 'alt', 'appetizer': 6, 'main': 7, 'dessert': 8})
res = requests.post(meals, headers=header, data=alt_dish)
res = delete_meal('alt')
print_res(res)
print()
