from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from marshmallow import Schema, fields
from database import Base, db_session



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    password = Column(String(12))
    balance = Column(Integer)

    def __repr__(self):
        return '<User %r>' % (self.name)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


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
    producable = fields.Nested(ProducableSchema, many=True, exclude=('basegoods', ), default=None)
    

class Producable(Base):
    __tablename__ = 'producables'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    price = Column(Float)
    time = Column(Integer)
    #goods = relationship('BaseGood', secondary=transaction, backref='Producable')
    blueprint = relationship('BaseGood', secondary='blueprints', backref='producables', lazy="joined")

    def __repr__(self):
        return '<Producable %r>' % (self.name)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    basegood_id = Column(Integer, ForeignKey('basegoods.id'))
    producable_id = Column(Integer, ForeignKey('producables.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    ammount = Column(Integer)
    action = Column(String)
    user = relationship(User, backref=backref("users_assoc"))
    basegood = relationship(BaseGood, backref=backref("basegoods_assoc"))
    producable = relationship(Producable, backref=backref("producables_assoc"))

class TransactionSchema(Schema):
    id = fields.Int(dump_only=True)
    basegood_id = fields.Int()
    producable_id = fields.Int()
    user_id = fields.Int()
    ammount = fields.Int()
    action = fields.Str()

class Blueprint(Base):
    __tablename__ = 'blueprints'
    id = Column(Integer, primary_key=True)
    basegood_id = Column(Integer, ForeignKey('basegoods.id'))
    producables_id = Column(Integer, ForeignKey('producables.id'))
    quantity = Column('quantity', Integer)

