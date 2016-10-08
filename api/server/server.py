from flask import Flask, jsonify
from flask_restful import Resource, Api
from database import init_db, db_session
from models import User, BaseGood, Producable, UserSchema, BaseGoodSchema, ProducableSchema

init_db()

app = Flask(__name__)
api = Api(app)


user_schema = UserSchema(many=True)
basegoods_schema = BaseGoodSchema(many=True)
basegood_schema = BaseGoodSchema()
producables_schema = ProducableSchema(many=True)
producable_schema = ProducableSchema()

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

@app.route("/producables/<int:pr>")
def get_producable(pr):
    try:
        producable = Producable.query.get(pr)
    except StandardError:
        return jsonify({"message": "Producable could not be found."}), 400
    result = producable_schema.dump(producable)
    #$producable_result = producables_schema.dump(basegood.producable)
    return jsonify({'basegood': result.data})



if __name__ == '__main__':
    app.run(debug=True)


@app.teardown_appcontext
def shutdown_session(exception=None):
        db_session.remove()

