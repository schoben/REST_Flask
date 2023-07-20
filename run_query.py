import requests
import json

port = '8000'
root = 'http://127.0.0.1:' + port
header = {'Content-Type': 'application/json'}
dishes = root + '/dishes'


def post_dish(name):
    return requests.post(dishes, headers=header, data=json.dumps({'name': name}))


def get_dish_by_name(name):
    return requests.get(dishes + '/' + name)


with open('query.txt') as f:
    foods = f.read().split('\n')

responses = []
for food in foods:
    post_dish(food)
    res = get_dish_by_name(food)
    responses.append(res)


with open('response.txt', 'w+') as f:
    for res in responses:
        res = res.json()
        string = f'{res["name"]} contains {res["cal"]} calories, {res["sodium"]} mgs of sodium, and {res["sugar"]} grams of sugar\n'
        f.write(string)