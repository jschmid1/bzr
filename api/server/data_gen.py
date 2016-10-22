from database import init_db, db_session
from faker import Factory
from models import User, BaseGood, Producable, Blueprint, Inventory, Season, BuildQueue
from random import randint
import logger

init_db()
fake = Factory.create()
logger.log.debug("Creating Fake entries")


basegoods = ['Iron', 'Copper', 'Wheat', 'Wood', 'Stone', 'Sand', 'Water']

producables = ['Tool', 'Road', 'Glass', 'House', 'Food']

max_user = 10
for times in range(0,max_user):
    if db_session.query(User).count() <= max_user:
        usr = User(name=fake.name(), email=fake.email(), password=fake.state(), balance=randint(1000,9000))
        db_session.add(usr)

db_session.commit()
for bg in basegoods:
    if db_session.query(BaseGood).filter(BaseGood.name == bg).count() == 0:
        basegood = BaseGood(name=bg, initprice=randint(1,25), price=randint(4,59))
        db_session.add(basegood)

db_session.commit()
for pb in producables:
    if db_session.query(Producable).filter(Producable.name == pb).count() == 0:
        prd = Producable(name=pb, price=randint(4,59), time=randint(100,1000))
        db_session.add(prd)

db_session.commit()
for prod in producables:
    # find producable by name -> get id
    # lookup in table to get the ammount and type
    # iterate over the basegoods
    # get quantity from table 
    prod_id = db_session.query(Producable).filter(Producable.name == prod).all()[0].id
    basegood_id = db_session.query(BaseGood).all()[randint(0,6)].id
    blueprint_one = Blueprint(basegood_id=basegood_id, producable_id=prod_id, quantity=5)
    db_session.add(blueprint_one)

for bg in basegoods:
    if db_session.query(Inventory).filter(BaseGood.name == bg).count() <= 0:
        basegood = BaseGood.query.filter(BaseGood.name == bg).first()
        all_users = User.query.all()
        for user in all_users:
            new_inv = Inventory(basegood=basegood, user_id=user.id, producable_id=None)
            db_session.add(new_inv)


user = User.query.get(1)


db_session.commit()
