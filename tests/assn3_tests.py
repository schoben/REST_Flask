import requests
import json


# Sources paths
port = '8000'
root = 'http://127.0.0.1:' + port
dishes = root + '/dishes'
meals = root + '/meals'
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


def get_meal(identifier):
    return requests.get(meals + '/' + identifier)


def delete_meal(identifier):
    return requests.delete(meals + '/' + identifier)


def get_all_meals():
    return requests.get(meals, headers=header)

# Verification functions
def print_res(res):
    print(res.json(), res)
    print()


def verify_res_json(res, json):
    assert res.json() == json


def verify_res_code(res, code):
    return res.status_code == code




#Tests
orange_id = None
foods = ['orange', 'spaghetti', 'apple pie']

def test_1():
    global orange_id
    ids = set()
    for food in foods:
        res = post_dish(food)
        ids.add(res.json())
        if food == 'orange':
            orange_id = res.json()
        assert verify_res_code(res, 201)
    assert len(ids) == len(foods)


def test_2():
    res = get_dish_by_idx(str(orange_id))
    assert verify_res_code(res, 200)
    res = res.json()
    assert res['sodium'] < 1.1
    assert res['sodium'] > 0.9


def test_3():
    res = get_all_dishes()
    assert verify_res_code(res, 200)
    assert len(res.json()) == len(foods)


def test_4():
    res = post_dish('blah')
    assert res.json() == -3
    assert res.status_code in [404, 400, 422]


def test_5():
    res = post_dish('orange')
    assert res.json() == -2
    assert res.status_code in [404, 400, 422]


def test_6():
    app = get_dish_by_name('orange').json()['ID']
    main = get_dish_by_name('spaghetti').json()['ID']
    des = get_dish_by_name('apple pie').json()['ID']
    delicious = json.dumps({'name': 'delicious', 'appetizer': app, 'main': main, 'dessert': des})
    res = requests.post(meals, headers=header, data=delicious)
    assert verify_res_code(res, 201)
    assert res.json() > 0


def test_7():
    res = get_all_meals()
    meal = res.json()
    assert verify_res_code(res, 200)
    assert len(meal) == 1
    cal = meal['1']['cal']
    assert cal < 500
    assert cal > 400


def test_8():
    app = get_dish_by_name('orange').json()['ID']
    main = get_dish_by_name('spaghetti').json()['ID']
    des = get_dish_by_name('apple pie').json()['ID']
    delicious = json.dumps({'name': 'delicious', 'appetizer': app, 'main': main, 'dessert': des})
    res = requests.post(meals, headers=header, data=delicious)
    assert res.status_code in [400, 422]
    assert res.json() == -2


def test_fail():
    assert False


# def test_missing_parameter():
#     app = get_dish_by_name('orange').json()['ID']
#     main = get_dish_by_name('spaghetti').json()['ID']
#     delicious = json.dumps({'name': 'delicious', 'appetizer': app, 'main': main})
#     res = requests.post(meals, headers=header, data=delicious)
#     assert res.status_code in [422]
#     assert res.json() == -1
#
# def test_media_not_sup():
#     app = get_dish_by_name('orange').json()['ID']
#     main = get_dish_by_name('spaghetti').json()['ID']
#     des = get_dish_by_name('apple pie').json()['ID']
#     delicious = json.dumps({'name': 'delicious', 'appetizer': app, 'main': main, 'dessert': des})
#     res = requests.post(meals, headers=None, data=delicious)
#     assert verify_res_code(res, 415)
#     assert res.json() == 0
