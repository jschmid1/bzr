from behave import given, when, then, step
import sure
from nose.tools import assert_equals
import time
import os
import json
from api.database.models import BaseGood, User, Producable
from seed import seed_users, seed_basegoods, seed_producables, create_links, fill_inventory, adding_seasons, adding_map
from api.database.db import db_session, db_path


@given(u'The system is set up properly')
def step_impl(context):
    seed_users()
    seed_basegoods()
    seed_producables()
    create_links()
    adding_seasons()
    adding_map()

@then(u'I wait for the system to catch up')
def step_impl(context):
    time.sleep(1)

@given(u'Some users are in the system')
def step_impl(context):
    seed_users()

@given(u'some basegoods are in the system')
def step_impl(context):
    seed_basegoods()

@given(u'some producables are in the system')
def step_impl(context):
    seed_producables()

@then(u'I spend all my money')
def step_impl(context):
    User.query.get(1).balance = 0
    db_session.commit()

@then(u'I make sure that the inventory is empty')
def step_impl(context):
    User.query.get(1).inventory = []
    db_session.commit()

@then(u'I retrieve the {resource} {res_id}')
def step_impl(context, resource, res_id):
    context.response = context.client.get("/{}/{}".format(resource, res_id))

@then(u'I retrieve all {resource}')
def step_impl(context, resource):
    context.response = context.client.get("/{}".format(resource))

@then(u'I buy the {resource} {res_id}')
def step_impl(context, resource, res_id):
    context.response = context.client.put('/{}/{}'.format(resource, res_id), data=json.dumps({'action': 'buy'}), content_type='application/json')
    
@then(u'my inventory should contain {resource} {res_id}')
def step_impl(context, resource, res_id):
    context.response = context.client.get('/users/1/inventory')
    good_name = None
    if (resource == 'producable'):
        good_name = Producable.query.get(res_id).name
    elif (resource == 'basegood'): 
        good_name = BaseGood.query.get(res_id).name
    else:
        raise "Not implemented"
    data = context.response.data
    print(data)
    print(User.query.get(1).inventory)
    payload = json.loads(data.decode('utf-8'))['inventory'][0][resource]
    payload.should.have.key('name').which.should.be.equal(good_name)

@then(u'I make sure that I have enough money')
def step_impl(context):
    User.query.get(1).balance = 99999
    db_session.commit()

@then(u'my inventory should not contain {resource} {res_id}')
def step_impl(context, resource, res_id):
    context.response = context.client.get('/users/1/inventory')
    good_name = None
    if (resource == 'producable'):
        good_name = Producable.query.get(res_id).name
    elif (resource == 'basegood'): 
        good_name = BaseGood.query.get(res_id).name
    else:
        raise "Not implemented"
    basegood_name = BaseGood.query.get(res_id).name
    data = context.response.data
    payload = json.loads(data.decode('utf-8'))['inventory']
    payload.should_not.have.key('name')
    
@then(u'I should get a {expected_status_code} response')
def step_impl(context, expected_status_code):
    assert_equals(context.response.status_code, int(expected_status_code))

@then(u'I should get a list of {resources}')
def step_impl(context, resources):
    data = context.response.data
    payload = json.loads(data.decode('utf-8'))[resources]
    payload.should.be.a(list)
    
@then(u'the following basegood details are returned')
def step_impl(context):
    data = context.response.data
    payload = json.loads(data.decode('utf-8'))['basegood']
    payload.should.have.key('initprice').which.should.be.an('float')
    payload.should.have.key('name').which.should.be.an('str')
    payload.should.have.key('id').which.should.be.an('int')

@then(u'the following user details are returned')
def step_impl(context):
    data = context.response.data
    payload = json.loads(data.decode('utf-8'))['user']
    payload.should.have.key('balance').which.should.be.a('float')
    payload.should.have.key('name').which.should.be.an('str')
    payload.should.have.key('id').which.should.be.an('int')


@then(u'the following producable details are returned')
def step_impl(context):
    data = context.response.data
    payload = json.loads(data.decode('utf-8'))['producable']
    payload.should.have.key('price').which.should.be.a('float')
    payload.should.have.key('name').which.should.be.an('str')
    payload.should.have.key('id').which.should.be.an('int')

@then(u'I try to produce the {resource} {res_id}')
def step_impl(context, resource, res_id):
    context.response = context.client.put('/{}/{}'.format(resource, res_id), data=json.dumps({'action': 'produce'}), content_type='application/json')

@then(u'my buildqueue should not contain that producable {res_id}')
def step_impl(context, res_id):
    context.response = context.client.get('/users/1/buildqueue')
    basegood_name = Producable.query.get(res_id).name
    data = context.response.data
    payload = json.loads(data.decode('utf-8'))['buildqueue']
    payload.should_not.have.key('name')

@then(u'I buy all the needed basegoods for producable {res_id}')
def step_impl(context, res_id):
    pr = Producable.query.get(res_id)
    for bg in pr.blueprint:
        context.response = context.client.put('/basegoods/{}'.format(bg.id), data=json.dumps({'action': 'buy'}), content_type='application/json')
    

@then(u'my buildqueue should contain that producable {res_id}')
def step_impl(context, res_id):
    context.response = context.client.get('/users/1/buildqueue')
    data = context.response.data
    payload = json.loads(data.decode('utf-8'))['buildqueue'][0]
    payload.should.have.key('id').which.should.be.an('int')

