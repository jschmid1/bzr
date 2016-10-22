from nose.tools import assert_true, assert_false
import requests


base_url = "http://localhost:5000/"

def test_users_response():
    response = requests.get(base_url+"users")
    assert_true(response.ok)

def test_one_user_response():
    response = requests.get(base_url+"users/1")
    assert_true(response.ok)

def test_one_basegood_response():
    response = requests.get(base_url+"basegoods/1")
    assert_true(response.ok)

def test_basegoods_response():
    response = requests.get(base_url+"basegoods")
    assert_true(response.ok)

def test_one_producable_response():
    response = requests.get(base_url+"producables/1") 
    assert_true(response.ok)

def test_producables_response():
    response = requests.get(base_url+"producables") 
    assert_true(response.ok)

def test_buildqueue_response():
    response = requests.get(base_url+"users/1/buildqueue") 
    assert_true(response.ok)

def test_inventory_response():
    response = requests.get(base_url+"users/1/inventory") 
    assert_true(response.ok)

def test_buy_basegood():
    response = requests.post(base_url+"basegoods/1/buy")
    assert_true(response.ok)

def test_sell_basegood():
    response = requests.post(base_url+"basegoods/1/sell")
    assert_true(response.ok)

def test_buy_producable():
    response = requests.post(base_url+"producable/1/buy")
    assert_true(response.ok)

def test_sell_producable():
    response = requests.post(base_url+"producable/1/sell")
    assert_true(response.ok)

def test_produce():
    response = requests.post(base_url+"producable/1/produce")
    assert_true(response.ok)



