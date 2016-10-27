from lettuce import step, world, before, after, after
from nose.tools import assert_equals
from api.server.server import app
import json
from api.database.models import BaseGood, User, Producable
from api.database.db_init import init_db, db_session, db_path
import sure
import os

init_db()
# redirect to testing db that gets destroyed after the run.

class ContextError(Exception):
    """Avoid deleting the development database if no Context is given"""
    

@before.all
def before_all():
    if 'development' in db_path or 'production' in db_path:
        raise ContextError("USE DB_ENV=testing lettuce ...")
    # rather call data_gen here
    world.app = app.test_client()
    bsg = BaseGood(name='Iron', initprice=42.2)
    db_session.add(bsg)
    bsg = BaseGood(name='Wood', initprice=41.1)
    db_session.add(bsg)
    bsg = BaseGood(name='Stone', initprice=0.0)
    db_session.add(bsg)
    prod = Producable(name='Tool', price=1)
    db_session.add(prod)
    usr = User(name='John', balance=42.2)
    db_session.add(usr)
    usr = User(name='Dasy', balance=41.1)
    db_session.add(usr)
    usr = User(name='The Dude', balance=0)
    db_session.add(usr)
    db_session.commit()

@after.all
def after_all(total):
    # rather than deleting it; clear the data.. 
    os.remove(db_path)

@step(u'When I retrieve the \'(.*)\' \'(.*)\'')
def when_i_retrieve_the_a_resource(step, resource, res_id):
    world.response = world.app.get('/{}/{}'.format(resource, res_id))

@step(u'When I retrieve all \'(.*)\'')
def when_i_retrieve_an_all_resource(step, resource):
    world.response = world.app.get('/{}'.format(resource))

@step(u'Then I should get a \'(.*)\' response')
def then_i_should_get_a_response(step, expected_status_code):
    assert_equals(world.response.status_code, int(expected_status_code))

@step(u'And I should get a list of \'(.*)\'')
def and_i_should_get_a_list_of_users(step, resource):
    payload = json.loads(world.response.data)[resource]
    payload.should.be.a(list)

@step(u'Given some \'(.*)\' are in the system')
def given_some_basegoods_are_in_the_system(step, resource):
    pass

@step(u'And the following basegood details are returned:')
def and_the_following_basegood_details(step):
    payload = json.loads(world.response.data)['basegood']
    payload.should.have.key('initprice').which.should.equal(42.2)
    payload.should.have.key('name').which.should.equal("Iron")
    payload.should.have.key('id').which.should.equal(1)

@step(u'And the following user details are returned:')
def and_the_following_user_details(step):
    payload = json.loads(world.response.data)['user']
    payload.should.have.key('balance').which.should.equal(42.2)
    payload.should.have.key('name').which.should.equal("John")
    payload.should.have.key('id').which.should.equal(1)

@step(u'And the following producable details are returned:')
def and_the_following_producable_details(step):
    payload = json.loads(world.response.data)['producable']
    payload.should.have.key('price').which.should.equal(1.0)
    payload.should.have.key('name').which.should.equal("Tool")
    payload.should.have.key('id').which.should.equal(1)


