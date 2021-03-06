from faker import Factory
from random import randint
from api.database.models import User, BaseGood, Producable, Blueprint, Inventory, Season, BuildQueue, Map, Effect, Event, Technology, EffectEvent, EffectTechnology 
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

basegoods = blueprints['Basegoods']
producables = blueprints['Producables']
max_users = blueprints['max_users']
events = blueprints['Events']
technologies = blueprints['Technologies']
effects = blueprints['Effects']

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


def add_basegood_to_inv(user_id, bg_id):
    user = db_session.query(User).filter(User.id == user_id).first()
    bg = BaseGood.query.get(1)
    new_inv = Inventory(basegood=bg, user_id=user.id, producable_id=None)
    db_session.add(new_inv)
    db_session.commit()


def seed_basegoods():
    log.debug("Seeding Basegoods")
    for bg in basegoods:
        if db_session.query(BaseGood).filter(BaseGood.name == bg).count() == 0:
            basegood = BaseGood(name=bg,
                                initprice=randint(1, 25),
                                price=randint(4, 59))
            db_session.add(basegood)
    db_session.commit()


def seed_producables():
    log.debug("Seeding Producables")
    for pb in producables:
        if db_session.query(Producable).filter(Producable.name == pb).count() == 0:
            prd = Producable(name=pb, price=randint(4,59), time=randint(5,10))
            db_session.add(prd)
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
        for prod in producables:
            # find producable by name -> get id
            # lookup in table to get the ammount and type
            # iterate over the basegoods
            # get quantity from table 
            prod_o = db_session.query(Producable).filter(Producable.name == prod).first()
            for bg in blueprints[prod]:
                #bg_name, quant = bg.items()[0] 
                # rather stupid python3
                bg_name = list(bg.keys())[0]
                quant = bg[bg_name]
                basegood_o = BaseGood.query.filter(BaseGood.name == bg_name).first()
                for i in range(quant):
                   blueprint = Blueprint(basegood_id=basegood_o.id, producable_id=prod_o.id)
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
    for bg in basegoods:
        if db_session.query(Inventory).filter(BaseGood.name == bg).count() <= 0:
            basegood = BaseGood.query.filter(BaseGood.name == bg).first()
            all_users = User.query.all()
            for user in all_users:
                new_inv = Inventory(basegood=basegood, user_id=user.id, producable_id=None)
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
        all_baseg = BaseGood.query.all()
        season = Season.query.first()
        map_o = MapGen(season, basegoods=all_baseg)
        map_o.generate()


def seed_all():
        seed_effects()
        seed_events()
        seed_technology()
        seed_users()
        link_effect_technology()
        link_effect_event()
        seed_basegoods()
        seed_producables()
        create_links()
        fill_inventory()
        adding_seasons()
        adding_map()

if __name__ == "__main__":
        # execute only if run as a script
        if 'testing' in db_path or 'test' in db_path:
            raise ValueError("Don't fill the testing Database")
        seed_all()
