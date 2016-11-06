from flask import Flask, jsonify, request, Response
from flask_restful import Resource, Api
import datetime
from api.database.models import User, BaseGood, Producable, UserSchema, BaseGoodSchema, ProducableSchema, Inventory, InventorySchema, BuildQueue, BuildQueueSchema
from api.database.db import init_db, db_session
from api.logger.logger import log
import json



log.debug("Initializing Database")
init_db()

app = Flask(__name__)
api = Api(app)


users_schema = UserSchema(many=True)
user_schema = UserSchema()
basegoods_schema = BaseGoodSchema(many=True)
basegood_schema = BaseGoodSchema()
producables_schema = ProducableSchema(many=True)
producable_schema = ProducableSchema()
inventory_schema = InventorySchema(many=True)
buildqueue_schema = BuildQueueSchema(many=True)

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

@app.errorhandler(409)
def insufficient_funds(error=None):
    message = {
            'status': 409,
            'message': 'Insufficient Funds: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 409 
    return resp


@app.route('/users', methods=['GET'])
def get_users():
    log.debug("Querying all Users")
    users = User.query.all()
    results = users_schema.dump(users)
    return jsonify({'users':results.data})

@app.route("/users/<int:usr>", methods=['GET'])
def get_user(usr):
    user = User.query.get(usr)
    if user is None:
        return not_found()
    results = user_schema.dump(user)
    return jsonify({'user':results.data})

@app.route('/basegoods', methods=['GET'])
def get_basegoods():
    basegoods = BaseGood.query.all()
    results = basegoods_schema.dump(basegoods)
    return jsonify({'basegoods':results.data})

@app.route("/basegoods/<int:bg>")
def get_basegood(bg):
    basegood = BaseGood.query.get(bg)
    if basegood is None:
        return not_found()
    basegood_result = basegood_schema.dump(basegood)
    return jsonify({'basegood': basegood_result.data})

@app.route('/producables', methods=['GET'])
def get_producables():
    producables = Producable.query.all()
    results = producables_schema.dump(producables)
    return jsonify({'producables':results.data})

@app.route("/producables/<int:pr>", methods=['GET'])
def get_producable(pr):
    producable = Producable.query.get(pr)
    if producable is None:
        return not_found()
    else:
        result = producable_schema.dump(producable)
        return jsonify({'producable': result.data})

# Technically this should return 202-Accepted.. 
# because it it not finished by the time the request is processed
def trigger_build(pr):
   current_user = User.query.get(1)
   producable = Producable.query.get(pr) 
   if producable is None:
       return not_found()
   inv = current_user.inv_expanded()
   for basegood in producable.basegoods:
       if basegood in inv:
           inv.remove(basegood)
       else:
           return insufficient_funds()
   for basegood in producable.basegoods:
        # .delete() is designed to bulk delete
        # .limit() does not work
        # .first() does not work
        # how to savely delete only one item? this is bad..
        inv = Inventory.query.\
                            filter(Inventory.user_id == current_user.id).\
                            filter(Inventory.basegood_id == basegood.id).first()
        Inventory.query.filter_by(id=inv.id).delete()

   build_queue = BuildQueue(user_id=current_user.id, 
              producable_id=producable.id,
              time_start = datetime.datetime.utcnow(),
              time_done = datetime.datetime.utcnow() )
   db_session.add(build_queue)
   db_session.commit()
   result = producable_schema.dump(producable)
   return jsonify({'producable': result.data})

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


def buy_basegood(bg):
    current_user = User.query.get(1)
    basegood = BaseGood.query.get(bg)
    if basegood is None:
        return not_found()
    pmap = current_user.season.pmap
    # Find the map object that has pmap.basegood.name => basegood.name
    corresp_map_object = [ map for map in pmap if map.basegood.name == basegood.name ][0]
    if current_user.has_enough_money_for(basegood):
        # and if basegood is still available -> check map_resoources
        if corresp_map_object.ammount < 1: # Change when bulk buys are implemented 
            return jsonify({'message': 'No more resources avaiable on map'})
        corresp_map_object.ammount -= 1
        inv = Inventory(user_id=current_user.id, basegood_id=basegood.id, producable_id=None)
        current_user.inventory.append(inv)
        current_user.balance -= basegood.price
        try:
            db_session.commit()
            return jsonify({'message': 'bought stuff'})
        except:
            return service_unavailabe()
    else:
        return insufficient_funds()

def sell_basegood(bg):
    current_user = User.query.get(1)
    basegood = BaseGood.query.get(bg)
    if basegood is None:
         return not_found()
    if basegood in current_user.inv_expanded():
        inv = Inventory.query.\
                            filter(Inventory.user_id == current_user.id).\
                            filter(Inventory.basegood_id == basegood.id).first()
        Inventory.query.filter_by(id=inv.id).delete()
        # .delete() is designed to bulk delete
        # .limit() does not work
        # .first() does not work
        # how to savely delete only one item? this is bad..
        try:
            db_session.commit()
            current_user.balance += basegood.price
            return jsonify({'message': 'sold stuff'})
        except:
            return service_unavailable()
    else:
        return jsonify({'message': 'you dont have what you want to sell'})

@app.route("/producables/<int:pr>", methods=['PUT'])
def handle_producable_puts(pr):
    if request.json['action'] == 'buy':
        return buy_producable(pr)
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
        inv = Inventory.query.\
                            filter(Inventory.user_id == current_user.id).\
                            filter(Inventory.producable_id == producable.id).first()
        Inventory.query.filter_by(id=inv.id).delete()
        try:
            db_session.commit()
            current_user.balance += producable.price
            return jsonify({'message': 'sold stuff'})
        except:
            return service_unavailable()
    else:
        return jsonify({'message': 'you dont have what you want to sell'})

def buy_producable(pr):
    # Check for general existence.
    current_user = User.query.get(1)
    producable = Producable.query.get(pr)
    if producable is None:
          return not_found()
    # check for users balance 
    if current_user.has_enough_money_for(producable):
        # and if basegood is still available -> check map_resoources
        inv = Inventory(user_id=current_user.id, basegood_id=None, producable_id=producable.id)
        current_user.inventory.append(inv)
        try:
            db_session.commit()
            current_user.balance -= producable.price
            db_session.commit()
            return jsonify({'message': 'bought producable'})
        except:
            return service_unavailabe()
    else:
        return insufficient_funds()

@app.route("/users/<int:usr>/inventory", methods=['GET'])
def get_inventory(usr):
    current_user = User.query.get(usr)
    if current_user is None:
        return not_found()
    results = inventory_schema.dump(current_user.inventory)
    return jsonify({'inventory': results.data})

@app.route("/users/<int:usr>/buildqueue", methods=['GET'])
def get_buildqueue(usr):
    current_user = User.query.get(usr)
    if current_user is None:
        return not_found()
    results = buildqueue_schema.dump(current_user.buildqueue)
    return jsonify({'buildqueue': results.data})

if __name__ == '__main__':
    app.run(debug=True)

@app.teardown_appcontext
def shutdown_session(exception=None):
        db_session.remove()

