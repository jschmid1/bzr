from flask import Flask, jsonify, request
from flask_restful import Api
from flask.ext.autodoc import Autodoc
import datetime
from api.database.db import init_db, db_session
from api.logger.logger import log
from api.database.models import User, Item,\
                                Technology, Event, Effect,\
                                UserSchema, ItemSchema,\
                                Inventory, Blueprint,\
                                InventorySchema, BuildQueue,\
                                BuildQueueSchema, BlueprintSchema,\
                                EventSchema, CapabilitiesSchema,\
                                EffectSchema, TechnologySchema
from flask_cors import CORS, cross_origin
from multiprocess import Process
import os
import calculations
import time
import multiprocessing

log.debug("Initializing Database")
init_db()

app = Flask(__name__)
api = Api(app)
auto = Autodoc(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


users_schema = UserSchema(many=True)
user_schema = UserSchema()
basegoods_schema = ItemSchema(many=True)
item_schema = ItemSchema()
blueprint_schema = BlueprintSchema()
inventory_schema = InventorySchema(many=True)
buildqueue_schema = BuildQueueSchema(many=True)
capabilities_schema = CapabilitiesSchema()
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

@app.errorhandler(409)
def producable_execption(error=None):
    message = {
            'status': 409,
            'message': 'You cant produce a baseitem like Stone or Water'
    }
    resp = jsonify(message)
    resp.status_code = 409
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
@auto.doc(groups=['public'])
def get_users():
    log.debug("Querying all Users")
    users = User.query.all()
    results = users_schema.dump(users)
    return jsonify({'users': results.data})

@app.route("/users/<int:usr>", methods=['GET'])
@auto.doc(groups=['public'])
def get_user(usr):
    user = User.query.get(usr)
    log.info("Querying user")
    if user is None:
        return not_found()
    results = user_schema.dump(user)
    return jsonify({'user': results.data})

@app.route("/events/<int:evt>", methods=['GET'])
@auto.doc(groups=['public'])
def get_event(evt):
    event = Event.query.get(evt)
    log.info("Querying event")
    if event is None:
        return not_found()
    results = event_schema.dump(event)
    return jsonify({'event': results.data})

@app.route("/effects/<int:efc>", methods=['GET'])
@auto.doc(groups=['public'])
def get_effect(efc):
    effect = Effect.query.get(efc)
    log.info("Querying effect")
    if effect is None:
        return not_found()
    results = effect_schema.dump(effect)
    return jsonify({'effect': results.data})

@app.route('/events', methods=['GET'])
@auto.doc(groups=['public'])
def get_events():
    log.info("Querying events")
    events = Event.query.all()
    results = events_schema.dump(events)
    return jsonify({'events': results.data})

@app.route('/effects', methods=['GET'])
@auto.doc(groups=['public'])
def get_effects():
    log.info("Querying effects")
    effects = Effect.query.all()
    results = effects_schema.dump(effects)
    return jsonify({'effects': results.data})

@app.route("/technologies/<int:tcn>", methods=['GET'])
@auto.doc(groups=['public'])
def get_technology(tcn):
    tech = Technology.query.get(tcn)
    log.info("Querying technology")
    if tech is None:
        return not_found()
    results = technology_schema.dump(tech)
    return jsonify({'technology': results.data})

@app.route('/technologies', methods=['GET'])
@auto.doc(groups=['public'])
def get_technologies():
    log.info("Querying technolgies")
    technologies = Technology.query.all()
    results = technologies_schema.dump(technologies)
    return jsonify({'techonologies': results.data})

@app.route('/items', methods=['GET'])
@auto.doc()
def get_items():
    log.info("Querying item")
    items = Item.query.all()
    results = basegoods_schema.dump(items)
    return jsonify({'item': results.data})

@app.route("/items/<int:bg>")
@auto.doc(groups=['public'])
def get_item(bg):
    log.info("Querying Item")
    item = Item.query.get(bg)
    if item is None:
        return not_found()
    item_result = item_schema.dump(item )
    return jsonify({'item': item_result.data})


@app.route("/items/<int:pr>/blueprint")
@auto.doc(groups=['public'])
def get_blueprint(pr):
    item = Item.query.get(pr)
    if item is None:
        return not_found()
    else:
        log.info("Querying blueprint for item {}".format(item.name))
        result = item.is_made_of_counter()
        ret_arr = []
        for item, counter in result.items():
            ret_arr.append({'item': item_schema.dump(item).data, 'ammount': counter})
        return jsonify(ret_arr)

#get_blueprint(16)

@app.route("/items/<int:bg>/capabilities")
@auto.doc(groups=['public'])
def get_capabilities(bg):
    basegood = Item.query.get(bg)
    if basegood is None:
        return not_found()
    else:
        log.info("Querying capabilities for basegood {}".format(basegood.name))
        result = capabilities_schema.dump(basegood)
        return jsonify({'basegood': result.data})

# Technically this should return 202-Accepted..
# because it it not finished by the time the request is processed
def trigger_build(itm):
    current_user = User.query.get(1)
    item = Item.query.get(itm)
    if item is None:
        return not_found()
    if item.category_id == 0:
        return producable_execption()
    log.info("Triggering build for {}".format(item.name))
    inv = current_user.inv_expanded()
    for item in item.is_made_of():
        if item in inv:
            # dont know if thats the best option ?
            # just count the respective len and ask the DB
            inv.remove(item)
        else:
            return insufficient_funds()
    for item in item.is_made_of():
        # .delete() is designed to bulk delete
        # .limit() does not work
        # .first() does not work
        # how to savely delete only one item? this is bad..
        inv = Inventory.query.\
                             filter(Inventory.user_id == current_user.id).\
                             filter(Inventory.item_id == item.id).\
                             first()
        Inventory.query.filter_by(id=inv.id).delete()
    try:
        bq_o = BuildQueue(user_id=current_user.id,
                          item_id=item.id,
                          time_start=datetime.datetime.utcnow(),
                          time_done=datetime.datetime.utcnow() +
                          datetime.timedelta(minutes=item.time),
                          active=False,
                          processed=False)
        db_session.add(bq_o)
        db_session.commit()
        result = item_schema.dump(item)
        return jsonify({'message': 'production initialized',
                        'item': result.data})
    except:
        return service_unavailable()


@app.route("/items/<int:itm>", methods=['PUT'])
@auto.doc(groups=['public'])
def handle_items_put(itm):
    if request.json is not None:
        # check for categories
        if request.json['action'] == 'buy':
            return buy_item(itm)
        if request.json['action'] == 'sell':
            return sell_item(itm)
        if request.json['action'] == 'produce':
            return trigger_build(itm)
    else:
        return not_found()



def buy_item(bg):
    current_user = User.query.get(1)
    item = Item.query.get(bg)
    if item is None:
        return not_found()
    log.info("Buying {}".format(item.name))
    pmap = current_user.season._map
    # Find the map object that has pmap.item.name => item.name
    if pmap:
        corresp_map_object = [map_o for map_o in pmap if map_o.item.name == item.name][0]
        if current_user.has_enough_money_for(item):
            # and if item is still available -> check map_resoources
            # Change when bulk buys are implemented
            if corresp_map_object.ammount < 1:
                return resource_exceeded()
            corresp_map_object.ammount -= 1
            inv = Inventory(user_id=current_user.id, item=item)
            current_user.inventory.append(inv)
            current_user.balance -= item.price
            try:
                db_session.commit()
                results = item_schema.dump(item)
                corresponding_map_object = [ x for x in pmap if x.id == bg ][0]
                new_price = calculations.new_price_test1(corresponding_map_object.initial_ammount, corresponding_map_object.ammount, item.init_price)
                item.price = new_price
                db_session.commit()
                return jsonify({'message': 'bought',
                                'item': results.data})
            except:
                return service_unavailable()
        else:
            return insufficient_funds()
    else:
            return resource_exceeded()


def sell_item(bg):
    current_user = User.query.get(1)
    item = Item.query.get(bg)
    pmap = current_user.season._map
    if item is None:
        return not_found()
    log.info("Selling {}".format(item.name))
    if item in current_user.inv_expanded():
        inv = Inventory.query.\
                            filter(Inventory.user_id == current_user.id).\
                            filter(Inventory.item_id == item.id).\
                            first()
        Inventory.query.filter_by(id=inv.id).delete()
        # .delete() is designed to bulk delete
        # .limit() does not work
        # .first() does not work
        # how to savely delete only one item? this is bad..
        try:
            current_user.balance += item.price_gen()
            if pmap:
                corresp_map_object = [map_o for map_o in pmap if map_o.item.name == item.name][0]
            corresp_map_object.ammount += 1
            results = item_schema.dump(item)
            db_session.commit()
            corresponding_map_object = [ x for x in pmap if x.id == bg ][0]
            if int(item.category) == 0:
                new_price = calculations.new_price_test1(corresponding_map_object.initial_ammount, corresponding_map_object.ammount, item.init_price)
                item.price = new_price
            db_session.commit()
            update_prices(item)
            return jsonify({'message': 'sold',
                            'item': results.data})
        except:
            return service_unavailable()
    else:
        return not_in_inv()

def update_prices(basegood):
    # that needs to be handled inside price_gen
    # with a recursive function call.
    # because it has to go down until category == 0
    if int(basegood.category) > 0:
        log.info("Updating prices after action on {}".format(basegood.name))
        basegood.price = basegood.price_gen()
        db_session.commit()


@app.route("/users/<int:usr>/inventory", methods=['GET'])
@auto.doc(groups=['public'])
def get_inventory(usr):
    current_user = User.query.get(usr)
    if current_user is None:
        return not_found()
    log.info("Querying inventory for user {}".format(current_user.name))
    results = inventory_schema.dump(current_user.inventory)
    
    return jsonify({'inventory': results.data})

@app.route("/users/<int:usr>/inventory/basegood/<int:bg>", methods=['GET'])
@auto.doc(groups=['public'])
def get_inventory_for_basegood(usr, bg):
    current_user = User.query.get(usr)
    bg = Item.query.get(bg)
    if current_user is None or bg is None:
        return not_found()
    log.info("Querying inventory for user {} and basegood {}".format(current_user.name, bg.name))
    inv = Inventory.query.\
                filter(Inventory.user_id == current_user.id).\
                filter(Inventory.basegood_id == bg.id).all()
    return jsonify({'basegood': item_schema.dump(bg), 'ammount': len(inv)})


@app.route("/users/<int:usr>/buildqueue", methods=['GET'])
@auto.doc(groups=['public'])
def get_buildqueue(usr):
    current_user = User.query.get(usr)
    if current_user is None:
        return not_found(basegood_idbasegood_id  )
    log.info("Querying buildqueue for user {}".format(current_user.name))
    results = buildqueue_schema.dump(current_user.buildqueue)
    return jsonify({'buildqueue': results.data})

@app.route('/documentation')
def documentation():
        return auto.html()

def run_server():
    app.run(debug=True)

if __name__ == '__main__':
    run_server()
    #n = multiprocessing.Process(name='wamp', target=run_wamp)
    #n.daemon = False
    #d = multiprocessing.Process(name='app', target=run_server)
    #d.daemon = False

    #d.start()
    #time.sleep(1)
    #n.start()

@app.teardown_appcontext
def shutdown_session(exception=None):
        db_session.remove()

