from faker import Factory
from random import randint
from api.database.models import User, Item, Blueprint, Inventory, Season, BuildQueue, Map, Effect, Event, Technology, EffectEvent, EffectTechnology, Category
from api.database.db import db_session, init_db, db_path
from api.logger.logger import log
from api.map_gen import MapGen
import datetime
import yaml
import os

#TODO: Move to to class context to adapt things more easily

if not os.path.isfile(db_path):
    init_db()

with open("api/config.yml", 'r') as stream:
    try:
        blueprints = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

items = blueprints['Items']
bp = blueprints['Blueprint']
max_users = blueprints['max_users']
events = blueprints['Events']
technologies = blueprints['Technologies']
effects = blueprints['Effects']
categories = blueprints['Categories']

def seed_events():
    if len(db_session.query(Event).all()) <= 0:
        log.debug("Adding Events")
        for evn in events:
            event = Event(name=evn)
            db_session.add(event)
        db_session.commit()

def seed_technology():
    if len(db_session.query(Technology).all()) <= 0:
        log.debug("Adding Technology")
        for tex in technologies:
            tech = Technology(name=tex)
            db_session.add(tech)
        db_session.commit()

def seed_users():
    log.debug("Seeding the Database")
    fake = Factory.create()

    log.debug("Seeding Users")
    for times in range(max_users):
        if db_session.query(User).count() <= max_users:
            usr = User(name=fake.name(),
                       email=fake.email(),
                       password=fake.state(),
                       balance=randint(1000, 9000))
            db_session.add(usr)
    db_session.commit()

def seed_categories():
    log.debug("Seed categories")
    for category in categories:
        for k, v in category.items():
            if db_session.query(Category).filter(Category.name == k).count() == 0:
                cat_o = Category(name=k, desc=v['desc'])
                db_session.add(cat_o)
    db_session.commit()

def seed_items():
    log.debug("Seeding items")
    for bg in items:
        for k, v in bg.items(): 
            if db_session.query(Item).filter(Item.name == k).count() == 0:
                item = Item(name=k,
                                    price = v['init_price'],
                                    init_price = v['init_price'],
                                    time = v['time'],
                                    category_id=v['category'])
                db_session.add(item)
    db_session.commit()

def add_item_to_inv(user_id, bg_id):
    user = db_session.query(User).filter(User.id == user_id).first()
    bg = Item.query.get(1)
    new_inv = Inventory(item=bg, user_id=user.id)
    db_session.add(new_inv)
    db_session.commit()


def seed_effects():
    if len(db_session.query(Effect).all()) <= 0:
        log.debug("Adding Effects")
        #if db_session.query(Effect).filter(Effect.name == effects[0]).count() == 0:
        for efc in effects:
            # the return here is:
            # {'FastProduction': [{'description': 'that'}, {'name': 'that'}]}
            # dict of array of dicts
            # currently disabled for simplification
            effect = Effect(name=efc)
            db_session.add(effect)
        db_session.commit()

def create_links():
    log.debug("Creating Blueprints")
    if len(db_session.query(Blueprint).all()) <= 0:
            for dct in bp:
                for item, recipe in dct.items():
                    recipe = recipe['needs']
                    item_o = Item.query.filter(Item.name == item).first()
                    for made_of, quant in recipe.items():
                        made_of_o = Item.query.filter(Item.name == made_of).first()
                        for i in range(quant):
                            blueprint = Blueprint(item_id=item_o.id, needs=made_of_o.id)
                            db_session.add(blueprint)
    db_session.commit()

def link_effect_event():
    log.debug("Linking Effects with Events")
    if len(db_session.query(EffectEvent).all()) <= 0:
        for event in events:
            event_o = db_session.query(Event).filter(Event.name == event).first()
            for effect in blueprints[event]:
                effect_o = Effect.query.filter(Effect.name == effect).first()
                effect_link = EffectEvent(event_id=event_o.id, effect_id=effect_o.id)
                db_session.add(effect_link)
        db_session.commit()

def link_effect_technology():
    log.debug("Linking Effects with Technologies")
    if len(db_session.query(EffectTechnology).all()) <= 0:
        for tech in technologies:
            tech_o = db_session.query(Technology).filter(Technology.name == tech).first()
            for effect in blueprints[tech]:
                effect_o = Effect.query.filter(Effect.name == effect).first()
                effect_link = EffectTechnology(technology_id=tech_o.id, effect_id=effect_o.id)
                db_session.add(effect_link)
        db_session.commit()

def fill_inventory():
    log.debug("Filling user inventories")
    for raw in items:
        for name, info in raw.items():
            if db_session.query(Inventory).filter(Item.name == name).count() <= 0:
                item = Item.query.filter(Item.name == name).first()
                all_users = User.query.all()
                for user in all_users:
                    new_inv = Inventory(item=item, user_id=user.id)
                    db_session.add(new_inv)
    db_session.commit()


def adding_seasons():
    log.debug("Adding users to Season")
    if Season.query.count() < 1:
        season_one = Season(season_start=datetime.datetime.utcnow(),
                            season_end=datetime.datetime.utcnow())
        db_session.add(season_one)
        db_session.commit()
    all_users = User.query.all()
    season = Season.query.first()
    for user in all_users:
        user.season_id = season.id
    db_session.commit()


def adding_map():
    log.debug("Generating a map")
    if Map.query.count() < 1:
        all_items = Item.query.all()
        season = Season.query.first()
        map_o = MapGen(season, items=all_items)
        map_o.generate()


def seed_all():
        seed_categories()
        seed_effects()
        seed_events()
        seed_technology()
        seed_users()
        link_effect_technology()
        link_effect_event()
        seed_items()
        create_links()
        fill_inventory()
        adding_seasons()
        adding_map()

if __name__ == "__main__":
        # execute only if run as a script
        if 'testing' in db_path or 'test' in db_path:
            raise ValueError("Don't fill the testing Database")
        seed_all()
