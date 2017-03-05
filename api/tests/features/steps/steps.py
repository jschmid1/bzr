from behave import given, when, then, step
import sure
from nose.tools import assert_equals
import time
import json
from api.database.models import BaseGood, User, Producable
from seed import seed_users, seed_basegoods, seed_producables, create_links, fill_inventory, adding_seasons, adding_map, add_basegood_to_inv
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


@then(u'I ask for the {what} of the {resource} {res_id}')
def step_impl(context, what, resource, res_id):
    context.response = context.client.get("/{}/{}/{}".format(resource, res_id, what))


@then(u'I retrieve the {resource} {res_id}')
def step_impl(context, resource, res_id):
    context.response = context.client.get("/{}/{}".format(resource, res_id))


@then(u'I retrieve all {resource}')
def step_impl(context, resource):
    context.response = context.client.get("/{}".format(resource))


# Behave does not allow the refactoring of {buy,sell,produce}
@then(u'I buy the {resource} {res_id}')
def step_impl(context, resource, res_id):
    context.response = context.client.put('/{}/{}'.format(resource, res_id),
                                          data=json.dumps({'action': 'buy'}),
                                          content_type='application/json')


@then(u'I sell the {resource} {res_id}')
def step_impl(context, resource, res_id):
    context.response = context.client.put('/{}/{}'.format(resource, res_id),
                                          data=json.dumps({'action': 'sell'}),
                                          content_type='application/json')


@then(u'I produce the {resource} {res_id}')
def step_impl(context, resource, res_id):
    context.response = context.client.put('/{}/{}'.format(resource, res_id),
                                          data=json.dumps({'action': 'produce'}),
                                          content_type='application/json')


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
    payload = json.loads(data.decode('utf-8'))['inventory'][0][resource]
    payload.should.have.key('name').which.should.be.equal(good_name)


@then(u'I make sure that I have enough money')
def step_impl(context):
    User.query.get(1).balance = 99999
    db_session.commit()

@then(u'I record the current price for a {}')
def step_impl(context, resource):
    # record the price before and after?
    # how to globally save them
    if resource == "producable":
        context.pr_price = Producable.query.get(1).price
    elif resource == "basegood":
        context.bg_price = BaseGood.query.get(1).price
    else:
        raise StandardError

@then(u'the price should be higher than before')
def step_impl(context):
    bg = BaseGood.query.get(1)
    bg.price.should.be.greater_than(context.old_price)

@then(u'the connected producables should be more expensive')
def step_impl(context):
    pr = Producable.query.get(1)
    pr.price.should.be.greater_than(context.old_pr_price)

@then(u'the connected producables should have the same price')
def step_impl(context):
    pr = Producable.query.get(1)
    pr.price.should.equal(context.old_pr_price)

@then(u'the price should be the same')
def step_impl(context):
    # record the price before and after?
    bg = BaseGood.query.get(1)
    bg.price.shouldnt.be.greater_than(context.old_price)
    bg.price.should.equal(context.old_price)

@then(u'my inventory should not contain {resource} {res_id}')
def step_impl(context, resource, res_id):
    context.response = context.client.get('/users/1/inventory')
    data = context.response.data
    payload = json.loads(data.decode('utf-8'))['inventory']
    payload.should_not.have.key('name')


@then(u'I should get a {expected_status_code} response')
def step_impl(context, expected_status_code):
    context.response.status_code.should.eql(int(expected_status_code))

@then(u'I see a list of basegoods')
def step_impl(context):
    data = context.response.data
    payload = json.loads(data.decode('utf-8'))
    payload.should.be.a(list)

@then(u'I see a nested list of {resources} in {outer}')
def step_impl(context, resources, outer):
    data = context.response.data
    payload = json.loads(data.decode('utf-8'))[outer][resources]
    payload.should.be.a(list)


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


@then(u'my buildqueue should not contain that producable {res_id}')
def step_impl(context, res_id):
    context.response = context.client.get('/users/1/buildqueue')
    data = context.response.data
    payload = json.loads(data.decode('utf-8'))['buildqueue']
    payload.should_not.have.key('name')


@then(u'I buy all the needed basegoods for producable {res_id}')
def step_impl(context, res_id):
    pr = Producable.query.get(res_id)
    for bg in pr.blueprint():
        context.response = context.client.put('/basegoods/{}'.format(bg.id),
                                              data=json.dumps({'action': 'buy'}),
                                              content_type='application/json')


@then(u'my buildqueue should contain that producable {res_id}')
def step_impl(context, res_id):
    context.response = context.client.get('/users/1/buildqueue')
    data = context.response.data
    payload = json.loads(data.decode('utf-8'))['buildqueue'][0]
    payload.should.have.key('id').which.should.be.an('int')


@then(u'I make sure that the basegood {res_id} is not present on the map')
def step_impl(context, res_id):
    User.query.get(1).season.pmap = []


@then(u'I expect "{message}" in the message')
def step_impl(context, message):
    data = context.response.data
    real_message = json.loads(data.decode('utf-8'))
    real_message.should.have.key('message').which.should.equal(message)


@then(u'I add the {resource} {res_id} to my inventory')
def step_impl(context, resource, res_id):
    add_basegood_to_inv(1, res_id)
