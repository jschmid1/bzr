from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from database import init_db, db_session
from models import User, BaseGood, Producable, UserSchema, BaseGoodSchema, ProducableSchema, Inventory,InventorySchema, BuildQueue
import datetime
import logger


logger.log.debug("Initializing Database")
init_db()

app = Flask(__name__)
api = Api(app)


user_schema = UserSchema(many=True)
basegoods_schema = BaseGoodSchema(many=True)
basegood_schema = BaseGoodSchema()
producables_schema = ProducableSchema(many=True)
producable_schema = ProducableSchema()
inventory_schema = InventorySchema()

@app.route('/users', methods=['GET'])
def get_users():
    logger.log.debug("Querying all Users")
    users = User.query.all()
    results = user_schema.dump(users)
    return jsonify({'users':results.data})

    
@app.route('/basegoods', methods=['GET'])
def get_basegoods():
    basegoods = BaseGood.query.all()
    results = basegoods_schema.dump(basegoods)
    return jsonify({'basegoods':results.data})

@app.route("/basegoods/<int:bg>")
def get_basegood(bg):
    try:
        basegood = BaseGood.query.get(bg)
    except StandardError:
        return jsonify({"message": "Basegood could not be found."}), 400
    basegood_result = basegood_schema.dump(basegood)
    return jsonify({'basegood': basegood_result.data})

@app.route('/producables', methods=['GET'])
def get_producables():
    producables = Producable.query.all()
    results = producables_schema.dump(producables)
    return jsonify({'producables':results.data})

@app.route("/producables/<int:pr>", methods=['GET'])
def get_producable(pr):
    try:
        producable = Producable.query.get(pr)
    #TODO Replace with real error message here
    except StandardError:
        return jsonify({"message": "Producable could not be found."}), 400
    result = producable_schema.dump(producable)
    return jsonify({'producable': result.data})


@app.route("/producable/<int:pr>/produce", methods=['POST'])
def trigger_build(pr):
   current_user = User.query.get(1)
   producable = Producable.query.get(pr) 
   inv = current_user.inv_expanded()
   for basegood in producable.basegoods:
       if basegood in inv:
           inv.remove(basegood)
       else:
           return jsonify({'message:': "Missing basegood"})
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


@app.route("/basegoods/<int:bg>/buy", methods=['POST'])
def buy_basegood(bg):
    current_user = User.query.get(1)
    basegood = BaseGood.query.get(bg)
    _map = current_user.season.pmap
    import pdb;pdb.set_trace()
    if current_user.has_enough_money_for(basegood):
        # and if basegood is still available -> check map_resoources
        inv = Inventory(user_id=current_user.id, basegood_id=basegood.id, producable_id=None)
        current_user.inventory.append(inv)
        current_user.balance -= basegood.price
        try:
            db_session.commit()
            return jsonify({'message': 'bought stuff'})
        except:
            return jsonify({'message': 'could not dump to database'})
    else:
        return jsonify({'message': 'Not enough money'})


@app.route("/basegoods/<int:bg>/sell", methods=['POST'])
def sell_basegood(bg):
    current_user = User.query.get(2)
    basegood = BaseGood.query.get(bg)
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
            return jsonify({'message': 'could not dump to database'})
    else:
        return jsonify({'message': 'you dont have what you want to sell'})


@app.route("/producable/<int:pr>/sell",methods=['POST'])
def sell_producable(pr):
    current_user = User.query.get(1)
    producable = Producable.query.get(pr)
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
            return jsonify({'message': 'could not dump to database'})
    else:
        return jsonify({'message': 'you dont have what you want to sell'})


@app.route("/producable/<int:pr>/buy", methods=['POST'])
def buy_producable(pr):
    # Check for general existence.
    current_user = User.query.get(1)
    producable = Producable.query.get(pr)
    # check for users balance 
    if current_user.has_enough_money_for(producable):
        # and if basegood is still available -> check map_resoources
        inv = Inventory(user_id=current_user.id, basegood_id=None, producable_id=producable.id)
        current_user.inventory.append(inv)
        try:
            db_session.commit()
            current_user.balance -= producable.price
            return jsonify({'message': 'bought producable'})
        except:
            return jsonify({'message': 'could not dump to database'})
    else:
        return jsonify({'message': 'Not enough money'})

@app.route("/user/<int:usr>/inventory", methods=['GET'])
def get_inventory(usr):
    current_user = User.query.get(usr)
    # This doesn't seem to work yet..TODO
    results = inventory_schema.dump(current_user.inventory)
    #import pdb;pdb.set_trace()
    return jsonify({'inventory': results.data})


if __name__ == '__main__':
    app.run(debug=True)


@app.teardown_appcontext
def shutdown_session(exception=None):
        db_session.remove()

