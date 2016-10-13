from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from database import init_db, db_session
from models import User, BaseGood, Producable, Transaction, UserSchema, BaseGoodSchema, ProducableSchema, TransactionSchema, Inventory, BuildQueue
import datetime

init_db()

app = Flask(__name__)
api = Api(app)


user_schema = UserSchema(many=True)
basegoods_schema = BaseGoodSchema(many=True)
basegood_schema = BaseGoodSchema()
producables_schema = ProducableSchema(many=True)
producable_schema = ProducableSchema()
transaction_schema = TransactionSchema()

@app.route('/users', methods=['GET'])
def get_users():
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
    #$producable_result = producables_schema.dump(basegood.producable)
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


@app.route("/producable/<int:pr>", methods=['POST'])
def trigger_build(pr):
   # dummy current_user = 1
   current_user = User.query.get(1)
   producable = Producable.query.get(pr) 
   # Check the inv of current_user.
   #import pdb;pdb.set_trace()
   for basegood in producable.basegoods:
       if not basegood in current_user.inventory:
           # return Flase if inv does not contain producable.blueprint
          # return jsonify({'message:': "Missing basegood"})
          pass
   for basegood in producable.basegoods:
       # Delete from inventory
       #current_user.inventory.remove(basegood.id)
       pass
   # Add to BuildQueue.
   build_queue = BuildQueue(user_id=current_user.id, 
              producables_id=producable.id,
              time_start = datetime.datetime.utcnow(),
              #o time_done = (datetime.datetime.now().time() + datetime.timedelta(minutes=producable.time)))
              time_done = datetime.datetime.utcnow() )
   db_session.add(build_queue)
   db_session.commit()
   result = producable_schema.dump(producable)
   return jsonify({'producable': result.data})


@app.route("/transaction/", methods=["POST"])
def make_transaction():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    data, errors = transaction_schema.load(json_data)
    if errors:
        return jsonify(errors), 422
    #TODO set defaults
    basegood_id = data['basegood_id']
    producable_id = data['producable_id']
    user_id = data['user_id']
    ammount = data['ammount']
    action = data['action']
    # OR rely on inventory
    transaction = Transaction(basegood_id=basegood_id,
                  producable_id=producable_id, 
                  user_id=user_id, 
                  ammount=ammount, 
                  action=action)
    
    db_session.add(transaction)
    db_session.commit()
    result = transaction_schema.dump(Transaction.query.get(transaction.id))
    return jsonify({"transaction": result.data})


if __name__ == '__main__':
    app.run(debug=True)


@app.teardown_appcontext
def shutdown_session(exception=None):
        db_session.remove()

