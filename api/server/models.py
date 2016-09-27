from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base, db_session

transaction = Table('transaction', Base.metadata,
    Column('basegoods_id', Integer, ForeignKey('basegoods.id')),
    Column('producables_id', Integer, ForeignKey('producables.id')),
    Column('users_id', Integer, ForeignKey('users.id')),
    Column('ammount', Integer),
    Column('action', String)
)


blueprint = Table('blueprint', Base.metadata,
    Column('basegoods_id', Integer, ForeignKey('basegoods.id')),
    Column('producables_id', Integer, ForeignKey('producables.id')),
    Column('quantity', Integer),
)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    password = Column(String(12))
    balance = Column(Integer)

    def __repr__(self):
        return '<User %r>' % (self.name)


class BaseGood(Base):
    __tablename__ = 'basegoods'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    initprice = Column(Float)
    price = Column(Float)
    producable = relationship('Producable', secondary=transaction, backref='BaseGood', lazy="dynamic")

    def __repr__(self):
        return '<BaseGood %r>' % (self.name)

class Producable(Base):
    __tablename__ = 'producables'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    price = Column(Float)
    time = Column(Integer)
    #goods = relationship('BaseGood', secondary=transaction, backref='Producable')
    blueprint = relationship('BaseGood', secondary=blueprint, backref='producables', lazy="dynamic")

    def __repr__(self):
        return '<Producable %r>' % (self.name)


