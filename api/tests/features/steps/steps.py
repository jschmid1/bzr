from behave import *
import sure
from nose.tools import assert_equals
import os
import json
from api.server import app
from api.database.models import BaseGood, User, Producable
from api.database.db import db_session, db_path
from api.seed import seed_users, seed_basegoods, seed_producables, create_links, fill_inventory, adding_seasons, adding_map


@given(u'Some users are in the system')
def step_impl(context):
    seed_users()

@when(u'call user one')
def step_impl(context):
    context.response = context.client.get('/users/1')#"/{}/{}".format(resource, res_id))

@then(u'I should get a {expected_status_code} response')
def step_impl(context, expected_status_code):
    assert_equals(context.response.status_code, int(expected_status_code))

@then(u'the following user details are returned')
def step_impl(context):
    payload = json.loads(context.response.data)['user']
    payload.should.have.key('balance').which.should.be.a('float')
    payload.should.have.key('name').which.should.be.an('unicode')
    payload.should.have.key('id').which.should.be.an('int')

