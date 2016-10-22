from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from marshmallow import Schema, fields
from database import Base, db_session



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    password = Column(String(12))
    balance = Column(Float())
    inventory = relationship("Inventory")

    def inv_expanded(self):
        return [ inv.basegood if inv.basegood else inv.producable for inv in self.inventory ]

    def has_enough_money_for(self, item):
        if self.balance >= item.price:
            return True
        else:
            return False

    def has_enough_in_inventory(self, list_of_items):
        pass

    def __repr__(self):
        return '<User %r>' % (self.name)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    balance = fields.Float()


class BaseGood(Base):
    __tablename__ = 'basegoods'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    initprice = Column(Float)
    price = Column(Float)
    producable = relationship('Producable', secondary='blueprints', backref='basegoods', lazy="joined")

    def __repr__(self):
        return '<BaseGood %r>' % (self.name)

class ProducableSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    price = fields.Float()
    time = fields.Int()
    basegoods = fields.Nested('BaseGoodSchema', many=True, exclude=('producable', ), default=None)
    

class BaseGoodSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    initprice = fields.Float()
    price = fields.Float()
    time = fields.DateTime()
    producable = fields.Nested(ProducableSchema, many=True, exclude=('basegoods', ), default=None)
    

class Producable(Base):
    __tablename__ = 'producables'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    price = Column(Float)
    time = Column(Integer)
    blueprint = relationship('BaseGood', secondary='blueprints', backref='producables', lazy="joined")

    def __repr__(self):
        return '<Producable %r>' % (self.name)

class Blueprint(Base):
    __tablename__ = 'blueprints'
    id = Column(Integer, primary_key=True)
    basegood_id = Column(Integer, ForeignKey('basegoods.id'))
    producable_id = Column(Integer, ForeignKey('producables.id'))
    quantity = Column('quantity', Integer)

class Inventory(Base):
    __tablename__ = 'inventorys'
    id = Column(Integer, primary_key=True)
    basegood_id = Column(Integer, ForeignKey('basegoods.id'))
    producable_id = Column(Integer, ForeignKey('producables.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    basegood = relationship(BaseGood, backref='inventory', lazy='joined')
    producable = relationship(Producable, backref='inventory', lazy='joined')

    def __repr__(self):
        if self.basegood:
            return '%r' % (self.basegood)
        else: 
            return '%r' % (self.producable)
#TODO
class InventorySchema(Schema):
    id = fields.Int(dump_only=True)
    basegood = fields.Nested(BaseGoodSchema, many=True, default=None)
    producable = fields.Nested(ProducableSchema, many=True, default=None)

# Who built what, when and when it's ready. Needs to be saved serverside
# to avoid hax.
class BuildQueue(Base):
    __tablename__ = 'buildqueue'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    producable_id = Column(Integer, ForeignKey('producables.id'))
    time_done = Column(DateTime)
    time_start = Column(DateTime)

class BuildQueueSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    producable_id = fields.Int()
    time_done = fields.Date()
    time_start = fields.Date()

class Season(Base):
    __tablename__ = 'season'
    id = Column(Integer, primary_key=True)
    season_start = Column(DateTime)
    season_end = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))

class SeasonSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    season_start = fields.Date()
    season_end = fields.Date()
