from api.database.db import Base, db_session
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from marshmallow import Schema, fields
from collections import Counter

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    password = Column(String(12))
    balance = Column(Float() )
    inventory = relationship("Inventory")
    buildqueue = relationship("BuildQueue")
    season_id = Column(Integer, ForeignKey('seasons.id'))
    season = relationship('Season')

    def inv_expanded(self):
        return [ inv.item for inv in self.inventory ]

    def has_enough_money_for(self, item):
        if self.balance >= item.price:
            return True
        else:
            return False

    def has_enough_in_inventory(self, list_of_items=[]):
        pass

    def __repr__(self):
        return '<User %r>' % (self.name)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    balance = fields.Float()

class BlueprintSchema(Schema):
    id = fields.Int(dump_only=True)
    items = fields.Nested('ItemSchema', many=True, default=None)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    desc = Column(String(500))

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    # that doesn't work yet..
    category = relationship(Category) #rel
    category_id = Column(Integer, ForeignKey('categories.id'))
    init_price = Column(Float)
    price = Column(Float) 
    time = Column(Float)
    # That only returns one :/
    #blueprint = relationship("Blueprint", back_populates="items", foreign_keys="[Blueprint.item_id]")

    def __repr__(self):
        return '<Item %r>' % (self.name)


    def is_made_of(self):
        # That's just dumb thoug.. back_populate should be enough
        items = Blueprint.query.filter_by(item_id=self.id).all()
        return [itm.needs_item for itm in items]

    def is_made_of_counter(self):
        # That's just dumb thoug.. back_populate should be enough
        items = Blueprint.query.filter_by(item_id=self.id).all()
        items = [itm.needs_item for itm in items]
        inf = dict(Counter(items))
        return inf

    def price_gen(self):
        blueprint = self.is_made_of_counter()
        if blueprint:
            price = 0
            for item, count in blueprint.items():
                for i in range(count):
                    price += item.price
        return price

        

class Blueprint(Base):
    __tablename__ = 'blueprints'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'))
    needs = Column(Integer, ForeignKey('items.id'))
    #items = relationship("Item", back_populates="blueprint", foreign_keys=[needs])
    needs_item = relationship(Item, backref='blueprint', lazy='joined', foreign_keys=[needs])

class ItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    category_id = fields.Str()
    initprice = fields.Float()
    price = fields.Float()
    time = fields.DateTime()

class CapabilitiesSchema(Schema):
#TODO: Fix .. doesn't work right now
    id = fields.Int(dump_only=True)
    name = fields.Str()
    initprice = fields.Float()
    price = fields.Float()
    time = fields.DateTime()
    producable = fields.Nested(ItemSchema, many=True, default=None)

class Inventory(Base):
    # nice spelling ..
    __tablename__ = 'inventorys'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    item = relationship(Item, backref='inventory', lazy='joined')
    #item_id = Column(Integer, ForeignKey('items.id'))
    #item = relationship('Item')

    def __repr__(self):
        return '%r' % (self.item)

class InventorySchema(Schema):
    id = fields.Int(dump_only=True)
    item = fields.Nested(ItemSchema, default=None)

class BuildQueue(Base):
    __tablename__ = 'buildqueue'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    item = relationship('Item')
    time_done = Column(DateTime)
    time_start = Column(DateTime)
    # To track history without comparing time. more efficient?
    active = Column(Boolean)
    # In case the server goes down, you can't judge if the itm was already processed
    processed = Column(Boolean)

class BuildQueueSchema(Schema):
    id = fields.Int(dump_only=True)
    item = fields.Nested(ItemSchema, default=None) 
    time_done = fields.Date()
    time_start = fields.Date()

class Season(Base):
    __tablename__ = 'seasons'
    id = Column(Integer, primary_key=True)
    season_start = Column(DateTime)
    season_end = Column(DateTime)
    _map = relationship('Map')

    def __repr__(self):
        return '<Season %r>' % (self.id)

class SeasonSchema(Schema):
    id = Column(Integer, primary_key=True)
    user_id = fields.Int()
    season_start = fields.Date()
    season_end = fields.Date()

class Map(Base):
    __tablename__ = 'maps'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'))
    item = relationship('Item')
    initial_ammount = Column(Integer)
    ammount = Column(Integer)
    season_id = Column(Integer, ForeignKey('seasons.id'))
    season = relationship('Season')

    def __repr__(self):
        return '<Map Info for %r>' % (self.item)

class MapSchema(Schema):
    id = fields.Int(dump_only=True)
    item = fields.Nested('ItemSchema', many=True, default=None)
    ammount = fields.Int()

class Technology(Base):
    __tablename__ = 'technologies'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    description = Column(String(500))
    effects = relationship('Effect', secondary='event_technology', backref='technologies', lazy="joined")

    def __repr__(self):
        return '<Technology %r>' % (self.name)

class TechnologySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String()
    description = fields.String()
    effects = fields.Nested('EffectSchema', many=True, default=None)

class Event(Base):
    # An Event affects either a BaseGood or 
    # a Producable witch an certain "Effect"
    # But a Event can have multiple Effects
    # -> n-m
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    description = Column(String(500))
    effects = relationship('Effect', secondary='effect_event', backref='events', lazy="joined")
    def __repr__(self):
        return '<Event %r>' % (self.name)

class Effect(Base):
    # An Effect does things like:
    # * lower a price
    # * accelerate the productiontime
    # * reduce the possibilty to have a failed
    __tablename__ = 'effects'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(500))
    # how to actually create events?
    # callbacks? but then how to map them to the corresponding class
    # map functions rather than a simple name and description
    def __repr__(self):
        return '<Effect %r>' % (self.name)

class EffectSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String()
    description = fields.String()

class EventSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String()
    description = fields.String()
    effects = fields.Nested(EffectSchema, many=True, default=None)

class EffectEvent(Base):
    __tablename__ = 'effect_event'
    id = Column(Integer, primary_key=True)
    ### Disabled basegood and prod for simplicity ####

    #basegood_id = Column(Integer, ForeignKey('basegoods.id'))
    #producable_id = Column(Integer, ForeignKey('producables.id'))

    ### Disabled basegood and prod for simplicity ####
    event_id = Column(Integer, ForeignKey('events.id'))
    effect_id = Column(Integer, ForeignKey('effects.id'))

class EffectTechnology(Base):
    __tablename__ = 'event_technology'
    id = Column(Integer, primary_key=True)
    ### Disabled basegood and prod for simplicity ####

    #basegood_id = Column(Integer, ForeignKey('basegoods.id'))
    #producable_id = Column(Integer, ForeignKey('producables.id'))

    ### Disabled basegood and prod for simplicity ####
    technology_id = Column(Integer, ForeignKey('technologies.id'))
    effect_id = Column(Integer, ForeignKey('effects.id'))
