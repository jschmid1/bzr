from flask import Flask, jsonify, request
from flask_restful import Api
import datetime
from api.database.db import init_db, db_session
from api.logger.logger import log
from api.database.models import User, BaseGood, Producable,\
                                Technology, Event, Effect,\
                                UserSchema, BaseGoodSchema,\
                                ProducableSchema, Inventory,\
                                InventorySchema, BuildQueue,\
                                BuildQueueSchema, BlueprintSchema,\
                                CapabilitiesSchema, EventSchema,\
                                EffectSchema, TechnologySchema
from flask_cors import CORS, cross_origin
from multiprocess import Process
import os
import calculations
import time
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from asyncio import sleep
from asyncio import coroutine
import multiprocessing

log.debug("Initializing Database")
init_db()

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


users_schema = UserSchema(many=True)
user_schema = UserSchema()
basegoods_schema = BaseGoodSchema(many=True)
basegood_schema = BaseGoodSchema()
producables_schema = ProducableSchema(many=True)
blueprint_schema = BlueprintSchema()
capabilities_schema = CapabilitiesSchema()
producable_schema = ProducableSchema()
inventory_schema = InventorySchema(many=True)
buildqueue_schema = BuildQueueSchema(many=True)
events_schema = EventSchema(many=True)
event_schema = EventSchema()
effect_schema = EffectSchema()
effects_schema = EffectSchema(many=True)
technology_schema = TechnologySchema()
technologies_schema = TechnologySchema(many=True)


@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


@app.errorhandler(503)
def service_unavailable(error=None):
    message = {
            'status': 503,
            'message': 'Service Unavailable: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 503
    return resp


# If GET instead PUT was used
@app.errorhandler(405)
def not_allowed(error=None):
    message = {
            'status': 405,
            'message': 'Method Not Allowed: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 405
    return resp


@app.errorhandler(403)
def forbidden(error=None):
    message = {
            'status': 403,
            'message': 'Forbidden: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 403
    return resp


# TODO: Add the basegood thats missing to the output
@app.errorhandler(409)
def insufficient_funds(error=None):
    message = {
            'status': 409,
            'message': 'Insufficient Funds: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 409
    return resp


@app.errorhandler(409)
def resource_exceeded(error=None):
    message = {
            'status': 409,
            'message': 'Resources exceeded on this map'
    }
    resp = jsonify(message)
    resp.status_code = 409
    return resp


@app.errorhandler(409)
def not_in_inv(error=None):
    message = {
            'status': 409,
            'message': 'You dont have what you want to sell'
    }
    resp = jsonify(message)
    resp.status_code = 409
    return resp

@app.route('/users', methods=['GET'])
def get_users():
    log.debug("Querying all Users")
    users = User.query.all()
    results = users_schema.dump(users)
    return jsonify({'users': results.data})

@app.route("/users/<int:usr>", methods=['GET'])
def get_user(usr):
    user = User.query.get(usr)
    log.info("Querying user")
    if user is None:
        return not_found()
    results = user_schema.dump(user)
    return jsonify({'user': results.data})

@app.route("/events/<int:evt>", methods=['GET'])
def get_event(evt):
    event = Event.query.get(evt)
    log.info("Querying event")
    if event is None:
        return not_found()
    results = event_schema.dump(event)
    return jsonify({'event': results.data})

@app.route("/effects/<int:efc>", methods=['GET'])
def get_effect(efc):
    effect = Effect.query.get(efc)
    log.info("Querying effect")
    if effect is None:
        return not_found()
    results = effect_schema.dump(effect)
    return jsonify({'effect': results.data})

@app.route('/events', methods=['GET'])
def get_events():
    log.info("Querying events")
    events = Event.query.all()
    results = events_schema.dump(events)
    return jsonify({'events': results.data})

@app.route('/effects', methods=['GET'])
def get_effects():
    log.info("Querying effects")
    effects = Effect.query.all()
    results = effects_schema.dump(effects)
    return jsonify({'effects': results.data})

@app.route("/technologies/<int:tcn>", methods=['GET'])
def get_technology(tcn):
    tech = Technology.query.get(tcn)
    log.info("Querying technology")
    if tech is None:
        return not_found()
    results = technology_schema.dump(tech)
    return jsonify({'technology': results.data})

@app.route('/technologies', methods=['GET'])
def get_technologies():
    log.info("Querying technolgies")
    technologies = Technology.query.all()
    results = technologies_schema.dump(technologies)
    return jsonify({'techonologies': results.data})

@app.route('/basegoods', methods=['GET'])
def get_basegoods():
    log.info("Querying basegoods")
    basegoods = BaseGood.query.all()
    results = basegoods_schema.dump(basegoods)
    return jsonify({'basegoods': results.data})

@app.route("/basegoods/<int:bg>")
def get_basegood(bg):
    log.info("Querying basegood")
    basegood = BaseGood.query.get(bg)
    if basegood is None:
        return not_found()
    basegood_result = basegood_schema.dump(basegood)
    return jsonify({'basegood': basegood_result.data})

@app.route('/producables', methods=['GET'])
def get_producables():
    log.info("Querying producables")
    producables = Producable.query.all()
    results = producables_schema.dump(producables)
    return jsonify({'producables': results.data})

@app.route("/producables/<int:pr>", methods=['GET'])
def get_producable(pr):
    producable = Producable.query.get(pr)
    if producable is None:
        return not_found()
    else:
        log.info("Querying producable")
        result = producable_schema.dump(producable)
        return jsonify({'producable': result.data})

@app.route("/producables/<int:pr>/blueprint")
def get_blueprint(pr):
    producable = Producable.query.get(pr)
    if producable is None:
        return not_found()
    else:
        log.info("Querying blueprint for producable {}".format(producable.name))
        result = producable.blueprint_dict()
        ret = {} 
        ret_arr = []
        for key, value in result.items():
            ret_arr.append({'basegood': basegood_schema.dump(key).data, 'ammount': value})
        return jsonify(ret_arr)


@app.route("/basegoods/<int:bg>/capabilities")
def get_capabilities(bg):
    basegood = BaseGood.query.get(bg)
    if basegood is None:
        return not_found()
    else:
        log.info("Querying capabilities for basegood {}".format(basegood.name))
        result = capabilities_schema.dump(basegood)
        return jsonify({'basegood': result.data})


# Technically this should return 202-Accepted..
# because it it not finished by the time the request is processed
def trigger_build(pr):
    current_user = User.query.get(1)
    producable = Producable.query.get(pr)
    if producable is None:
        return not_found()
    log.info("Triggering build for {}".format(producable.name))
    inv = current_user.inv_expanded()
    for basegood in producable.blueprint():
        if basegood in inv:
            # dont know if thats the best option ?
            # just count the respective len and ask the DB
            inv.remove(basegood)
        else:
            return insufficient_funds()
    for basegood in producable.blueprint():
        # .delete() is designed to bulk delete
        # .limit() does not work
        # .first() does not work
        # how to savely delete only one item? this is bad..
        inv = Inventory.query.\
                             filter(Inventory.user_id == current_user.id).\
                             filter(Inventory.basegood_id == basegood.id).\
                             first()
        Inventory.query.filter_by(id=inv.id).delete()
    try:
        build_queue = BuildQueue(user_id=current_user.id,
                                 producable_id=producable.id,
                                 time_start=datetime.datetime.utcnow(),
                                 time_done=datetime.datetime.utcnow() +
                                 datetime.timedelta(minutes=producable.time),
                                 active=False,
                                 processed=False)
        db_session.add(build_queue)
        db_session.commit()
        result = producable_schema.dump(producable)
        return jsonify({'message': 'production initialized',
                        'producable': result.data})
    except:
        return service_unavailable()


@app.route("/basegoods/<int:bg>", methods=['PUT'])
def handle_basegood_puts(bg):
    if request.json is not None:
        if request.json['action'] == 'buy':
            return buy_basegood(bg)
        if request.json['action'] == 'sell':
            return sell_basegood(bg)
        else:
            return not_found()
    else:
        return not_found()

def calculate_new_prod_price(affected_producables=[]):
    for pr in affected_producables:
        unique_bg_list = pr.blueprint()
        # reduce the list to unique items first
        new_price = 0
        for bg in unique_bg_list:
            new_price += bg.price
        try:
            new_price_after_multi = (new_price * (pr.time - (pr.time/5)))
            log.debug('adapted Price for {} from previous {} to {}'.format(pr.name, pr.price, new_price_after_multi))
            # Plus some extra money that acts
            # as salary for the 'work'
            # this can depend on the pr.time
            pr.price = new_price_after_multi
            db_session.commit()
        except:
            log.debug('Something went wrong during the price calculation of Producables')


def buy_basegood(bg):
    current_user = User.query.get(1)
    basegood = BaseGood.query.get(bg)
    if basegood is None:
        return not_found()
    log.info("Buying {}".format(basegood.name))
    pmap = current_user.season.pmap
    # Find the map object that has pmap.basegood.name => basegood.name
    if pmap:
        corresp_map_object = [map_o for map_o in pmap if map_o.basegood.name == basegood.name][0]
        if current_user.has_enough_money_for(basegood):
            # and if basegood is still available -> check map_resoources
            # Change when bulk buys are implemented
            if corresp_map_object.ammount < 1:
                return resource_exceeded()
            corresp_map_object.ammount -= 1
            inv = Inventory(user_id=current_user.id,
                            basegood_id=basegood.id,
                            producable_id=None)
            current_user.inventory.append(inv)
            current_user.balance -= basegood.price
            try:
                db_session.commit()
                results = basegood_schema.dump(basegood)
                corresponding_map_object = [ x for x in pmap if x.id == bg ][0]
                new_price = calculations.new_price_test1(corresponding_map_object.initial_ammount, corresponding_map_object.ammount, basegood.initprice)
                basegood.price = new_price
                db_session.commit()
                calculate_new_prod_price(basegood.producable)
                return jsonify({'message': 'bought',
                                'basegood': results.data})
            except:
                return service_unavailable()
        else:
            return insufficient_funds()
    else:
            return resource_exceeded()


def sell_basegood(bg):
    current_user = User.query.get(1)
    basegood = BaseGood.query.get(bg)
    pmap = current_user.season.pmap
    if basegood is None:
        return not_found()
    log.info("Selling {}".format(basegood.name))
    if basegood in current_user.inv_expanded():
        inv = Inventory.query.\
                            filter(Inventory.user_id == current_user.id).\
                            filter(Inventory.basegood_id == basegood.id).\
                            first()
        Inventory.query.filter_by(id=inv.id).delete()
        # .delete() is designed to bulk delete
        # .limit() does not work
        # .first() does not work
        # how to savely delete only one item? this is bad..
        try:
            current_user.balance += basegood.price
            if pmap:
                corresp_map_object = [map_o for map_o in pmap if map_o.basegood.name == basegood.name][0]
            corresp_map_object.ammount += 1
            results = basegood_schema.dump(basegood)
            db_session.commit()
            corresponding_map_object = [ x for x in pmap if x.id == bg ][0]
            new_price = calculations.new_price_test1(corresponding_map_object.initial_ammount, corresponding_map_object.ammount, basegood.initprice)
            basegood.price = new_price
            calculate_new_prod_price(basegood.producable)
            db_session.commit()
            return jsonify({'message': 'sold',
                            'basegood': results.data})
        except:
            return service_unavailable()
    else:
        return not_in_inv()


@app.route("/producables/<int:pr>", methods=['PUT'])
def handle_producable_puts(pr):
    if request.json['action'] == 'buy':
        # return buy_producable(pr)
        # Not Allowed
        return not_allowed()
        pass
    elif request.json['action'] == 'sell':
        return sell_producable(pr)
    elif request.json['action'] == 'produce':
        return trigger_build(pr)
    else:
        return not_found()


def sell_producable(pr):
    current_user = User.query.get(1)
    producable = Producable.query.get(pr)
    if producable is None:
        return not_found()
    if producable in current_user.inv_expanded():
        log.info("Selling {}".format(producable.name))
        inv = Inventory.query.\
                            filter(Inventory.user_id == current_user.id).\
                            filter(Inventory.producable_id == producable.id).\
                            first()
        Inventory.query.filter_by(id=inv.id).delete()
        try:
            db_session.commit()
            current_user.balance += producable.price
            results = producable_schema.dump(producable)
            return jsonify({'message': 'sold',
                            'producable': results.data})
        except:
            return service_unavailable()
    else:
        return not_in_inv()


def buy_producable(pr):
    current_user = User.query.get(1)
    producable = Producable.query.get(pr)
    if producable is None:
        return not_found()
    log.info("Buying {}".format(producable.name))
    # TODO: Only allow to buy from a CPU.
    # CPU has it's own inventory
    if current_user.has_enough_money_for(producable):
        inv = Inventory(user_id=current_user.id,
                        basegood_id=None,
                        producable_id=producable.id)
        current_user.inventory.append(inv)
        try:
            current_user.balance -= producable.price
            db_session.commit()
            results = producable_schema.dump(producable)
            return jsonify({'message': 'bought',
                            'producable': results.data})
        except:
            return service_unavailable()
    else:
        return insufficient_funds()


@app.route("/users/<int:usr>/inventory", methods=['GET'])
def get_inventory(usr):
    current_user = User.query.get(usr)
    if current_user is None:
        return not_found()
    log.info("Querying inventory for user {}".format(current_user.name))
    results = inventory_schema.dump(current_user.inventory)
    
    return jsonify({'inventory': results.data})

@app.route("/users/<int:usr>/inventory/basegood/<int:bg>", methods=['GET'])
def get_inventory_for_basegood(usr, bg):
    current_user = User.query.get(usr)
    bg = BaseGood.query.get(bg)
    if current_user is None or bg is None:
        return not_found()
    log.info("Querying inventory for user {} and basegood {}".format(current_user.name, bg.name))
    inv = Inventory.query.\
                filter(Inventory.user_id == current_user.id).\
                filter(Inventory.basegood_id == bg.id).all()
    return jsonify({'basegood': basegood_schema.dump(bg), 'ammount': len(inv)})

@app.route("/users/<int:usr>/inventory/producable/<int:pr>", methods=['GET'])
def get_inventory_for_producable(usr, pr):
    pr = Producable.query.get(pr)
    current_user = User.query.get(usr)
    if current_user is None or pr is None:
        return not_found()
    log.info("Querying inventory for user {} and producable {}".format(current_user.name, pr.name))
    inv = Inventory.query.\
                filter(Inventory.user_id == current_user.id).\
                filter(Inventory.producable_id == pr.id).all()
    return jsonify({'producable': producable_schema.dump(pr), 'ammount': len(inv)})

@app.route("/users/<int:usr>/buildqueue", methods=['GET'])
def get_buildqueue(usr):
    current_user = User.query.get(usr)
    if current_user is None:
        return not_found(basegood_idbasegood_id  )
    log.info("Querying buildqueue for user {}".format(current_user.name))
    results = buildqueue_schema.dump(current_user.buildqueue)
    return jsonify({'buildqueue': results.data})

@app.route("/users/<int:usr>/buildqueue/producable/<int:pr>", methods=['GET'])
def get_buildqueue_for(usr,pr):
    current_user = User.query.get(usr)
    pr = Producable.query.get(pr)
    if current_user is None or pr is None:
        return not_found()
    queue = BuildQueue.query.\
            filter(BuildQueue.processed == False).\
            filter(BuildQueue.user_id == current_user.id).\
            filter(BuildQueue.producable_id == pr.id).all()
    return jsonify({'producable': buildqueue_schema.dump(queue).data, 'ammount': len(queue)})


def run_server():
    app.run(debug=True)

if __name__ == '__main__':
    #n = multiprocessing.Process(name='wamp', target=run_wamp)
    #n.daemon = False
    d = multiprocessing.Process(name='app', target=run_server)
    d.daemon = False

    d.start()
    #time.sleep(1)
    #n.start()

@app.teardown_appcontext
def shutdown_session(exception=None):
        db_session.remove()
