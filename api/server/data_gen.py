from database import init_db, db_session
from faker import Factory
from models import User, BaseGood, Producable, Blueprint, Transaction
from random import randint

init_db()
fake = Factory.create()

basegoods = ['Iron', 'Copper', 'Wheat', 'Wood', 'Stone', 'Sand', 'Water']

producables = ['Tool', 'Road', 'Glass', 'House', 'Food']

max_user = 10
for times in range(0,max_user):
    if db_session.query(User).count() <= max_user:
        usr = User(name=fake.name(), email=fake.email(), password=fake.state(), balance=randint(0,9))
        db_session.add(usr)

db_session.commit()
for bg in basegoods:
    if db_session.query(BaseGood).filter(BaseGood.name == bg).count() == 0:
        basegood = BaseGood(name=bg, initprice=randint(1,25))
        db_session.add(basegood)

db_session.commit()
for pb in producables:
    if db_session.query(Producable).filter(Producable.name == pb).count() == 0:
        prd = Producable(name=pb, time=randint(100,1000))
        db_session.add(prd)

db_session.commit()
for prod in producables:
    # find producable by name -> get id
    # lookup in table to get the ammount and type
    # iterate over the basegoods
    # get quantity from table 
    prod_id = db_session.query(Producable).filter(Producable.name == prod).all()[0].id
    basegood_id = db_session.query(BaseGood).all()[0].id
    blueprint_one = Blueprint(basegood_id=basegood_id, producables_id=prod_id, quantity=5)
    db_session.add(blueprint_one)
    pass

import pdb;pdb.set_trace()
db_session.commit()
