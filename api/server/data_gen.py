from database import init_db, db_session
from faker import Factory
from models import User, BaseGood, Producable
from random import randint

init_db()
fake = Factory.create()

basegoods = ['Iron', 'Copper', 'Wheat', 'Wood', 'Stone', 'Sand', 'Water']

producables = ['Tool', 'Road', 'Glass', 'House', 'Food']

import pdb;pdb.set_trace()
for times in range(1,10):
    # if size ^ -> range has not been reached 
    usr = User(name=fake.name(), email=fake.email(), password=fake.state(), balance=randint(0,9))
    db_session.add(usr)

for bg in basegoods:
    if db_session.query(BaseGood).filter(BaseGood.name == bg) is None:
        basegood = BaseGood(name=bg, initprice=randint(1,25))
        db_session.add(basegood)

for pb in producables:
    if db_session.query(Producable).filter(Producable.name == pb) is None:
        prd = Producable(name=pb, time=randint(100,1000))
        db_session.add(prd)


db_session.commit()
#import pdb; pdb.set_trace()
