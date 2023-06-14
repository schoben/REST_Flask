#Tests for Meals
import requests
import json

port = '5000'
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



post_dish('salad')
post_dish('steak')
post_dish('ice cream')
print(f"Printing all existing dishes at this point:")
print_res(get_all_dishes())


#Adding a first meal
print(f"Adding a meal. Should return 0")
meals = root + '/meals'
basic_meal = json.dumps({'name': 'basic', 'appetizer': 0, 'main': 1, 'dessert': 2})
res = requests.post(meals, headers=header, data=basic_meal)
print_res(res)
#
#
# Test: Getting all meals. Should have a single 'basic' meal.
def get_all_meals():
    return requests.get(meals, headers=header)


print(f"Printing all available meals:")
res = get_all_meals()
print(res.json())
print()

print("Adding a hamburger dish")
res = post_dish('hamburger')
print_res(res)
print()


print(f"updating a meal. Should return 0")
meals_0 = root + '/meals/0'
basic_meal = json.dumps({'name': 'basic', 'appetizer': 0, 'main': 3, 'dessert': 2})
res = requests.put(meals_0, headers=header, data=basic_meal)
print_res(res)


def get_meal(identifier):
    return requests.get(meals + '/' + identifier)

def delete_meal(identifier):
    return requests.delete(meals + '/' + identifier)


# Getting a meal by index
print(f"Getting meal of index 0")
res = get_meal('0')
print_res(res)
print()


# Getting a meal by name
print(f"Getting meal by name 'basic'")
res = get_meal('basic')
print_res(res)
print()

#
# Delete meal by index
print(f"Deleteing meal of index 0")
res = delete_meal('0')
print_res(res)
print()


# Delete meal by name
print(f"Deleteing meal of index basic")
res = delete_meal('basic')
print_res(res)
print()



# print(f"Adding a bread dish")
# res = post_dish('bread')
# print_res(res)
# print()
#
#
# print("Adding a hamburger dish")
# res = post_dish('hamburger')
# print_res(res)
# print()