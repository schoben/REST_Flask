"""
Client module for testing
"""


import requests
import json


# Sources paths
port = '5002'
root = 'http://127.0.0.1:' + port
diets = root + '/diets'
header = {'Content-Type': 'application/json'}

# Function for communicating with server
def get_all_diets():
    return requests.get(diets)

def post_diet(name, cal, sodium, sugar):
    return requests.post(diets, headers=header, data=json.dumps({'name': name, 'cal': cal, 'sodium': sodium, 'sugar': sugar}))

def post_missing_diet(name, cal, sodium):
    return requests.post(diets, headers=header, data=json.dumps({'name': name, 'cal': cal, 'sodium': sodium}))

def get_diet_by_name(name):  # TODO: remove this or previous func
    return requests.get(diets + '/' + name)

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


print(f"Test: Adding a 'health' diet. Should return 'Diet health was created successfully' with code 201")
res = post_diet('health', 2000, 200, 50)
print_res(res)
verify_res_code(res, 201)

print(f"Test: Adding a 'medium' diet. Should return 'Diet health was created successfully' with code 201")
res = post_diet('medium', 2000, 500, 50)
print_res(res)
verify_res_code(res, 201)

print(f"Test: getting a 'fake' diet. Should return 'Diet fake not found' with code 404")
res = get_diet_by_name('fake')
print_res(res)

print(f"Test: Adding'health' diet again. Should return 'Diet with health already exists' with code 422")
res = post_diet('health', 2000, 200, 50)
print_res(res)
verify_res_code(res, 422)

print(f"Test: Retrieve all diets, should receive a json of all diets with code 200")
res = get_all_diets()
print_res(res)
verify_res_code(res, 200)
#
print(f"Test: test missing attribute, should return 'Incorrect POST format', 422")
res = post_missing_diet('junk', 4000, 400)
print_res(res)
verify_res_code(res, 422)
#
print(f"Test: retrieve diet by name, should return json for health, 200")
res = get_diet_by_name('health')
print_res(res)

root = 'http://127.0.0.1:' + '80'
print(f"Test: get meals with diet by name, should empty json array, 200")
meals = root + '/meals'
res = requests.get(meals+'?diet=health')
print_res(res)

print(f"Test: get meals with diet by name, should json array with meals, 200")
meals = root + '/meals'
res = requests.get(meals+'?diet=medium')
print_res(res)

#TODO test missing application json if time permits - post request on diets resource